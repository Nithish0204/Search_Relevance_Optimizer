"""
Dynamic reference data registry.
Loads brands, colors, and categories from Elasticsearch using aggregation queries.

Cached in memory with configurable TTL (default 5 minutes).
Auto-refreshes when cache expires. Falls back to empty lists if ES is unavailable.

Usage:
    from nlp.registry import get_brands, get_colors, get_categories

    brands     = get_brands()      # → ["boat", "nike", "samsung", ...]
    colors     = get_colors()      # → ["black", "red", "blue", ...]
    categories = get_categories()  # → ["headphones", "shoes", "mobiles", ...]
"""

import time
import os
from elasticsearch import Elasticsearch
from nlp.config import ES_HOST, ES_INDEX

# cache TTL in seconds (default 5 minutes, configurable via env)
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# ── internal cache ────────────────────────────────────────────────

_cache = {
    "brands":     [],
    "colors":     [],
    "categories": [],
    "last_refresh": 0,
}

def _is_cache_stale() -> bool:
    """Check if cached data is older than CACHE_TTL."""
    return (time.time() - _cache["last_refresh"]) > CACHE_TTL

def _fetch_distinct_values(es: Elasticsearch, field: str, size: int = 500) -> list:
    """
    Fetch distinct values of a field from ES using terms aggregation.

    Args:
        es    : Elasticsearch client
        field : field name to aggregate (e.g., "brand", "color", "category")
        size  : max number of distinct values to return

    Returns:
        list of lowercase unique values, e.g. ["boat", "nike", "samsung"]
    """
    try:
        resp = es.search(
            index=ES_INDEX,
            body={
                "size": 0,
                "aggs": {
                    f"unique_{field}": {
                        "terms": {
                            "field": field,
                            "size": size
                        }
                    }
                }
            }
        )
        buckets = resp["aggregations"][f"unique_{field}"]["buckets"]
        return [b["key"].lower().strip() for b in buckets if b["key"].strip()]
    except Exception:
        return []

def refresh_registry() -> None:
    """
    Reload brands, colors, and categories from Elasticsearch.
    Called automatically when cache is stale. Can also be called manually.

    If ES is unavailable, cache stays empty — pipeline still works,
    it just won't extract brands/colors/categories from queries.
    ES search handles matching via BM25 + kNN regardless.
    """
    try:
        es = Elasticsearch(ES_HOST)
        if not es.ping():
            print("[Registry] ES not reachable — using empty cache")
            return

        _cache["brands"]     = _fetch_distinct_values(es, "brand")
        _cache["colors"]     = _fetch_distinct_values(es, "color")
        _cache["categories"] = _fetch_distinct_values(es, "category.keyword")
        _cache["last_refresh"] = time.time()

        print(f"[Registry] Loaded {len(_cache['brands'])} brands, "
              f"{len(_cache['colors'])} colors, "
              f"{len(_cache['categories'])} categories from ES")

    except Exception as e:
        print(f"[Registry] Failed to refresh from ES: {e}")

def _ensure_fresh() -> None:
    """Refresh cache if stale."""
    if _is_cache_stale():
        refresh_registry()

# ── public API ────────────────────────────────────────────────────

def get_brands() -> list:
    """Get list of known brands from ES (cached)."""
    _ensure_fresh()
    return _cache["brands"]

def get_colors() -> list:
    """Get list of known colors from ES (cached)."""
    _ensure_fresh()
    return _cache["colors"]

def get_categories() -> list:
    """Get list of known categories from ES (cached)."""
    _ensure_fresh()
    return _cache["categories"]

def force_refresh() -> None:
    """Force an immediate cache refresh (bypass TTL)."""
    _cache["last_refresh"] = 0
    refresh_registry()
