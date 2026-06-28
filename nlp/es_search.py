"""
Hybrid Elasticsearch search.
Combines BM25 keyword search + kNN vector search using manual RRF.

Runs two separate ES queries (BM25 + kNN), then merges them in Python
via Reciprocal Rank Fusion. Works on the free/basic ES license.

Main function:
    search_products(parsed: ParsedQuery, query_vector: list) → list[dict]
"""

from elasticsearch import Elasticsearch
from nlp.models import ParsedQuery
from nlp.config import ES_HOST, ES_INDEX

def _build_filters(parsed: ParsedQuery) -> tuple:
    """
    Build ES filter clauses and boost clauses from ParsedQuery.
    
    Returns (hard_filters, soft_boosts):
      - hard_filters: price, brand, gender, color, rating — strict constraints
      - soft_boosts: category — preference, not exclusion
    
    Category is a SOFT BOOST so that "earbuds" ranks earbuds first
    but also shows related products like headphones.
    """
    filters = []
    boosts = []

    if parsed.price_max:
        filters.append({"range": {"price": {"lte": parsed.price_max}}})
    if parsed.price_min:
        filters.append({"range": {"price": {"gte": parsed.price_min}}})
    if parsed.brand:
        filters.append({"term": {"brand": parsed.brand.lower()}})
    if parsed.category:
        # Category is a SOFT BOOST — ranks matching category higher
        # but doesn't exclude other categories
        boosts.append({"term": {"category.keyword": {"value": parsed.category.lower(), "boost": 5}}})
    if parsed.gender:
        filters.append({"term": {"gender": parsed.gender}})
    if parsed.color:
        boosts.append({"term": {"color": {"value": parsed.color, "boost": 2}}})
    if parsed.rating_min:
        filters.append({"range": {"rating": {"gte": parsed.rating_min}}})

    return filters, boosts

def _build_bm25_query(parsed: ParsedQuery) -> dict:
    """
    Build BM25 keyword query.
    multi_match on title^3, category^2, description^1 with fuzziness.
    Category is used as a soft boost (should), not a hard filter.
    """
    filters, boosts = _build_filters(parsed)
    keyword_str = " ".join(parsed.keywords) if parsed.keywords else ""

    query = {
        "size": 50,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query":     keyword_str or "*",
                        "fields":    ["title^3", "category^2", "description^1"],
                        "fuzziness": "AUTO:5,8",  # Only fuzzy-match words ≥5 chars
                        "type":      "best_fields"
                    }
                },
                "filter": filters,
                "should": boosts
            }
        }
    }
    return query

def _build_knn_query(parsed: ParsedQuery, query_vector: list) -> dict:
    """
    Build kNN vector search query.
    Cosine similarity on the embedding field (HNSW index).
    Only hard filters (price, brand, gender) are applied — not category boost.
    """
    filters, _ = _build_filters(parsed)

    query = {
        "size": 50,
        "knn": {
            "field":          "embedding",
            "query_vector":   query_vector,
            "k":              50,
            "num_candidates": 100,
        }
    }

    # apply hard filters to knn block
    if filters:
        query["knn"]["filter"] = {"bool": {"filter": filters}}

    return query

def _reciprocal_rank_fusion(
    bm25_hits: list,
    knn_hits: list,
    k: int = 60,
    top_n: int = 20,
) -> list:
    """
    Merge two ranked lists using Reciprocal Rank Fusion (RRF).

    RRF score = Σ  1 / (k + rank_i)

    This is the same algorithm ES uses internally with `rank: {rrf: {}}`,
    but computed in Python so it works on the free/basic license.

    Args:
        bm25_hits : list of ES hit dicts from BM25 query
        knn_hits  : list of ES hit dicts from kNN query
        k         : rank constant (default 60, same as ES default)
        top_n     : max results to return

    Returns:
        list of product source dicts, ranked by fused score.
    """
    scores = {}   # doc_id → rrf_score
    docs   = {}   # doc_id → _source dict

    for rank, hit in enumerate(bm25_hits, start=1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id]   = hit["_source"]

    for rank, hit in enumerate(knn_hits, start=1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id]   = hit["_source"]

    # sort by fused score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [docs[doc_id] for doc_id, _ in ranked[:top_n]]

def search_products(parsed: ParsedQuery, query_vector: list) -> list:
    """
    Run hybrid search and return ranked product list.

    Executes BM25 and kNN as two separate queries, then merges
    results using manual Reciprocal Rank Fusion (RRF) in Python.

    Args:
        parsed       : ParsedQuery — output of parse_query()
        query_vector : list[float] — output of get_query_vector()

    Returns:
        list of product dicts ranked by hybrid BM25 + cosine score.
        Returns [] if ES is unavailable (never crashes the caller).

    Example:
        from nlp.parser import parse_query
        from nlp.vectorizer import get_query_vector
        from nlp.es_search import search_products

        parsed  = parse_query("airpods under 2k")
        vector  = get_query_vector(parsed.keywords, "airpods under 2k")
        results = search_products(parsed, vector)
    """
    es = Elasticsearch(ES_HOST)
    try:
        # run both queries separately
        bm25_query = _build_bm25_query(parsed)
        knn_query  = _build_knn_query(parsed, query_vector)

        bm25_resp = es.search(index=ES_INDEX, body=bm25_query)
        knn_resp  = es.search(index=ES_INDEX, body=knn_query)

        bm25_hits = bm25_resp["hits"]["hits"]
        # Drop kNN hits with very low cosine similarity to prevent "returning everything"
        # ES scales cosine to (1 + cosine)/2. A score < 0.65 means cosine < 0.30
        knn_hits = [hit for hit in knn_resp["hits"]["hits"] if hit["_score"] >= 0.60]

        # merge with RRF
        return _reciprocal_rank_fusion(bm25_hits, knn_hits)

    except Exception as e:
        print(f"[ES Search Error] {e}")
        return []   # never crash the backend route
