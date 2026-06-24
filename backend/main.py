import time
from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bson import ObjectId
from database import products_collection
from parser import extract_filters

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


async def index_to_elasticsearch(mongo_id: str, product: dict):
    
    try:
        print(f"[stub] would index product {mongo_id} into Elasticsearch")
        
    except Exception as e:
        products_collection.database["sync_failures"].insert_one({
            "mongo_id": mongo_id,
            "error": str(e)
        })


@app.post("/products")
def add_product(product: Product, bg: BackgroundTasks):
    result = products_collection.insert_one(product.dict())
    mongo_id = str(result.inserted_id)
    bg.add_task(index_to_elasticsearch, mongo_id, product.dict())
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
def search_products_route(q: str = Query(..., min_length=1, max_length=200)):
    cache_key = q.lower().strip()
    cached = get_cached(cache_key)
    if cached:
        return cached

    filters = extract_filters(q)
    results = []
    for r in products_collection.find(filters):
        r["id"] = str(r["_id"])
        del r["_id"]
        results.append(r)

    response = {
        "results": results,
        "total": len(results),
        "query": q,
        "filters_applied": filters,
        "corrected_query": None  # will come from real parser later
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
        "total_brands": len(brands)
    }
