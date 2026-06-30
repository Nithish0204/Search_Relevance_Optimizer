"""
Index a single product + its embedding into Elasticsearch.
Designed to be called from a FastAPI BackgroundTask.
Logs failures to MongoDB sync_failures collection.

Usage (how backend will call this later):
    background_tasks.add_task(index_product, mongo_id, product_dict, db)
"""

from elasticsearch import Elasticsearch
from nlp.vectorizer import get_product_vector
from nlp.config import ES_HOST, ES_INDEX
from datetime import datetime

async def index_product(mongo_id: str, product: dict, db=None):
    """
    Generate embedding and index product into Elasticsearch.

    Args:
        mongo_id : str  — MongoDB _id as string
        product  : dict — full product document
        db       : Motor async db instance (optional — for failure logging)

    This function is async so FastAPI can call it as a BackgroundTask.
    If ES fails, logs to MongoDB sync_failures — never crashes silently.
    """
    es = Elasticsearch(ES_HOST)
    try:
        embedding = get_product_vector(product)

        doc = {
            "mongo_id":    mongo_id,
            "title":       product.get("title",       ""),
            "brand":       product.get("brand",       "").lower(),
            "category":    product.get("category",    ""),
            "color":       product.get("color",       ""),
            "gender":      product.get("gender",      ""),
            "description": product.get("description", ""),
            "price":       float(product.get("price",    0)),
            "rating":      float(product.get("rating",   0)),
            "discount":    int(product.get("discount",   0)),
            "stock":       int(product.get("stock",      0)),
            "embedding":   embedding
        }

        es.index(index=ES_INDEX, id=mongo_id, document=doc)
        print(f"[ES Indexer] ✓ Indexed: {product.get('title', mongo_id)}")

    except Exception as e:
        print(f"[ES Indexer] ✗ Failed: {mongo_id} — {e}")
        if db is not None:
            try:
                await db["sync_failures"].insert_one({
                    "mongo_id":  mongo_id,
                    "error":     str(e),
                    "timestamp": datetime.utcnow()
                })
            except Exception:
                pass
