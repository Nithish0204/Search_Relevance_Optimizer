"""
Text vectorization using Sentence Transformers.
Model is loaded ONCE at module level — never inside a per-call function.

Two functions:
    get_product_vector(product: dict) → list[float]  — for indexing
    get_query_vector(keywords, raw)   → list[float]  — for searching
"""

from sentence_transformers import SentenceTransformer
from nlp.config import MODEL_NAME

# loaded once when this module is first imported (~3 seconds, then cached)
_model = SentenceTransformer(MODEL_NAME)

def _product_text(product: dict) -> str:
    """
    Build embed input from product fields.
    Title + category + first 50 words of description only.
    (Model truncates at 256 tokens — short focused input = better vectors)
    """
    title    = str(product.get("title",       "")).strip()
    category = str(product.get("category",    "")).strip()
    desc     = " ".join(str(product.get("description", "")).split()[:50])
    return f"{title} {category} {desc}".strip()

def get_product_vector(product: dict) -> list:
    """
    Generate 384-dim embedding for a product.
    Call this when indexing a product into Elasticsearch.

    Example:
        product = {"title": "boAt Rockerz 450", "category": "headphones", ...}
        vector  = get_product_vector(product)
        # → [0.12, -0.34, 0.08, ...] (384 floats)
    """
    text = _product_text(product)
    return _model.encode(text).tolist()

def get_query_vector(keywords: list, raw_query: str = "") -> list:
    """
    Generate 384-dim embedding for a search query.
    Uses joined keywords. Falls back to raw_query if keywords empty.

    Example:
        keywords    = ["airpods", "wireless"]
        query_vector = get_query_vector(keywords)
        # → [0.09, -0.22, 0.41, ...] (384 floats)
    """
    text = " ".join(keywords).strip() if keywords else raw_query.strip()
    if not text:
        text = raw_query
    return _model.encode(text).tolist()

def batch_encode(texts: list) -> list:
    """
    Encode a list of texts in batches.
    Used by bulk_index.py for efficient mass indexing.

    Returns list of vectors (each a list of 384 floats).
    """
    embeddings = _model.encode(texts, batch_size=32, show_progress_bar=True)
    return [emb.tolist() for emb in embeddings]

def get_model():
    """Return the loaded model (for bulk operations)."""
    return _model
