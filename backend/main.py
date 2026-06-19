from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from database import products_collection
from parser import extract_filters

class Product(BaseModel):
    title: str
    category: str
    color: str
    price: float
    gender: str
    rating: float
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
    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        return {"success": False, "message": "Product not found"}
    product["id"] = str(product["_id"])
    del product["_id"]
    return {"success": True, "product": product}


@app.post("/products")
def add_product(product: Product):
    result = products_collection.insert_one(product.dict())
    return {"success": True, "message": "Product added successfully", "id": str(result.inserted_id)}


@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    result = products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": product.dict()}
    )
    if result.matched_count == 0:
        return {"success": False, "message": "Product not found"}
    return {"success": True, "message": "Product updated successfully"}


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    result = products_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        return {"success": False, "message": "Product not found"}
    return {"success": True, "message": "Product deleted successfully"}


@app.get("/search")
def search_products(q: str):
    filters = extract_filters(q)
    results = []
    for r in products_collection.find(filters):
        r["id"] = str(r["_id"])
        del r["_id"]
        results.append(r)
    return {"query": q, "filters_applied": filters, "results": results}


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