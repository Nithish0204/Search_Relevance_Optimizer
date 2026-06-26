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


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products")
def get_products():
    products = []
    for p in products_collection.find({}):
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


@app.post("/products")
def add_product(product: Product, bg: BackgroundTasks):
    result = products_collection.insert_one(product.dict())
    mongo_id = str(result.inserted_id)
    bg.add_task(run_index_product, mongo_id, product.dict())
    bg.add_task(force_refresh)
    return {"success": True, "message": "Product added successfully", "id": mongo_id}


@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    try:
        result = products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": product.dict()}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    if result.matched_count == 0:
        return {"success": False, "message": "Product not found"}
    return {"success": True, "message": "Product updated successfully"}


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    try:
        result = products_collection.delete_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    if result.deleted_count == 0:
        return {"success": False, "message": "Product not found"}
    return {"success": True, "message": "Product deleted successfully"}


@app.get("/search")
def search_products_route(
    q: str = Query(..., min_length=1, max_length=200),
    brand: str = Query(None),
    rating: float = Query(None)
):
    cache_key = f"{q.lower().strip()}|{brand}|{rating}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    parsed = parse_query(q)
    
    # Override NLP if user explicitly selected a UI filter
    if brand:
        parsed.brand = brand.lower()
    if rating:
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
    
    # Capitalize for UI display
    categories_ui = [c.title() for c in categories if c]
    brands_ui = [b.title() for b in brands if b]
    
    return {
        "total_products": total_products,
        "total_categories": len(categories),
        "total_brands": len(brands),
        "categories": categories_ui,
        "brands": brands_ui
    }
