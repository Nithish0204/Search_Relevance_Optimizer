import time
from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bson import ObjectId
from database import products_collection
from database import products_collection
import sys
import os
import asyncio

# Add project root to Python path so we can import the nlp module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.parser import parse_query
from nlp.vectorizer import get_query_vector
from nlp.es_search import search_products
from nlp.es_indexer import index_product
from nlp.registry import force_refresh

class Product(BaseModel):
    title: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    color: str
    price: float = Field(..., gt=0)
    gender: str
    rating: float = Field(..., ge=0, le=5)
    brand: str
    in_stock: bool
    image_url: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SEARCH_CACHE = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_cached(key: str):
    entry = SEARCH_CACHE.get(key)
    if not entry:
        return None
    cached_time, value = entry
    if time.time() - cached_time > CACHE_TTL_SECONDS:
        del SEARCH_CACHE[key]
        return None
    return value


def set_cache(key: str, value: dict):
    SEARCH_CACHE[key] = (time.time(), value)


def clear_cache():
    SEARCH_CACHE.clear()

@app.on_event("startup")
def sync_databases_on_startup():
    """
    Automatically clean up Elasticsearch on server startup.
    If the server crashed while deleting a product, this removes the 'ghost' from ES.
    """
    from elasticsearch import Elasticsearch
    from pymongo import MongoClient
    from nlp.config import MONGO_URI, MONGO_DB, ES_HOST, ES_INDEX

    try:
        # Get all valid IDs from MongoDB
        client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
        db = client[MONGO_DB]
        mongo_ids = set(str(p["_id"]) for p in db["products"].find({}, {"_id": 1}))

        # Find and delete orphaned docs in Elasticsearch
        es = Elasticsearch(ES_HOST)
        if es.ping():
            resp = es.search(index=ES_INDEX, body={"size": 1000, "query": {"match_all": {}}})
            hits = resp["hits"]["hits"]
            deleted_count = 0
            
            for hit in hits:
                if hit["_id"] not in mongo_ids:
                    es.delete(index=ES_INDEX, id=hit["_id"])
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 [Auto-Sync] Cleaned up {deleted_count} orphaned products from Elasticsearch.")
            else:
                print("✨ [Auto-Sync] Databases are perfectly in sync.")
    except Exception as e:
        print(f"⚠️ [Auto-Sync] Failed to sync databases on startup: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products")
def get_products(brand: str = None, rating: float = None):
    query = {}
    if brand:
        query["brand"] = brand.lower()
    if rating is not None:
        query["rating"] = {"$gte": rating}
        
    products = []
    for p in products_collection.find(query):
        p["id"] = str(p["_id"])
        del p["_id"]
        products.append(p)
    return {"count": len(products), "products": products}


@app.get("/products/{product_id}")
def get_single_product(product_id: str):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    if not product:
        return {"success": False, "message": "Product not found"}
    product["id"] = str(product["_id"])
    del product["_id"]
    return {"success": True, "product": product}


def run_index_product(mongo_id: str, product_dict: dict):
    """Wrapper to run the async index_product function in a separate event loop"""
    asyncio.run(index_product(mongo_id, product_dict, None))

def run_delete_es_product(mongo_id: str):
    """Delete a product from Elasticsearch in background"""
    from elasticsearch import Elasticsearch
    from nlp.config import ES_HOST, ES_INDEX
    try:
        es = Elasticsearch(ES_HOST)
        es.delete(index=ES_INDEX, id=mongo_id)
        print(f"[ES] Deleted {mongo_id}")
    except Exception as e:
        print(f"[ES] Failed to delete {mongo_id}: {e}")

@app.post("/products")
def add_product(product: Product, bg: BackgroundTasks):
    result = products_collection.insert_one(product.dict())
    mongo_id = str(result.inserted_id)
    bg.add_task(run_index_product, mongo_id, product.dict())
    bg.add_task(force_refresh)
    clear_cache()
    return {"success": True, "message": "Product added successfully", "id": mongo_id}


@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product, bg: BackgroundTasks):
    try:
        result = products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": product.dict()}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    if result.matched_count == 0:
        return {"success": False, "message": "Product not found"}
    
    # Sync with ES and clear cache
    bg.add_task(run_index_product, product_id, product.dict())
    bg.add_task(force_refresh)
    clear_cache()
    return {"success": True, "message": "Product updated successfully"}


@app.delete("/products/{product_id}")
def delete_product(product_id: str, bg: BackgroundTasks):
    try:
        result = products_collection.delete_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    if result.deleted_count == 0:
        return {"success": False, "message": "Product not found"}
        
    # Sync with ES and clear cache
    bg.add_task(run_delete_es_product, product_id)
    bg.add_task(force_refresh)
    clear_cache()
    return {"success": True, "message": "Product deleted successfully"}


@app.get("/search")
def search_products_route(
    q: str = Query(..., min_length=1, max_length=200),
    brand: str = None,
    rating: float = None
):
    cache_key = f"{q.lower().strip()}_b:{brand}_r:{rating}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    parsed = parse_query(q)
    
    # Override with explicit UI filters if provided
    if brand:
        parsed.brand = brand
    if rating is not None:
        parsed.rating_min = rating
        
    vector = get_query_vector(parsed.keywords, q)
    results = search_products(parsed, vector)

    response = {
        "results": results,
        "total": len(results),
        "query": q,
        "corrected_query": parsed.corrected_query
    }
    set_cache(cache_key, response)
    return response


@app.get("/stats")
def get_stats():
    total_products = products_collection.count_documents({})
    categories = products_collection.distinct("category")
    brands = products_collection.distinct("brand")
    return {
        "total_products": total_products,
        "total_categories": len(categories),
        "total_brands": len(brands),
        "categories": categories,
        "brands": brands
    }
