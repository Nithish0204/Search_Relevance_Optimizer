"""
Bulk index ALL existing MongoDB products into Elasticsearch.
Run this ONCE after create_es_index.py.

Usage:
    python -m nlp.bulk_index
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from motor.motor_asyncio import AsyncIOMotorClient
from nlp.vectorizer import batch_encode, _product_text
from nlp.config import ES_HOST, ES_INDEX, MONGO_URI, MONGO_DB
import asyncio

async def fetch_products() -> list:
    client = AsyncIOMotorClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    cursor = client[MONGO_DB]["products"].find({})
    return await cursor.to_list(length=None)

def make_actions(products: list) -> list:
    texts = [_product_text(p) for p in products]
    print(f"Encoding {len(texts)} products in batches...")
    embeddings = batch_encode(texts)

    actions = []
    for product, emb in zip(products, embeddings):
        mongo_id = str(product["_id"])
        actions.append({
            "_index": ES_INDEX,
            "_id":    mongo_id,
            "_source": {
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
                "embedding":   emb
            }
        })
    return actions

async def main():
    print("Fetching products from MongoDB...")
    products = await fetch_products()
    if not products:
        print("No products found in MongoDB.")
        return

    print(f"Found {len(products)} products.")
    actions         = make_actions(products)
    es              = Elasticsearch(ES_HOST)
    success, failed = bulk(es, actions, raise_on_error=False)

    print(f"\nDone. Indexed: {success} | Failed: {len(failed)}")
    for f in failed:
        print(f"  FAILED: {f}")

if __name__ == "__main__":
    asyncio.run(main())
