import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from elasticsearch import Elasticsearch

from nlp.config import MONGO_URI, MONGO_DB, ES_HOST, ES_INDEX
from nlp.es_indexer import index_product
from nlp.registry import force_refresh
from nlp.parser import parse_query
from nlp.vectorizer import get_query_vector
from nlp.es_search import search_products

SAMPLE_PRODUCTS = [
    {
        "title": "boAt Airdopes 141 True Wireless",
        "brand": "boat", "category": "earbuds", "color": "black",
        "gender": "unisex", "description": "Bluetooth wireless earbuds with 42H playtime",
        "price": 1299, "rating": 4.1, "discount": 20, "stock": 200,
    },
    {
        "title": "Nike Air Max 270 Sneakers",
        "brand": "nike", "category": "sneakers", "color": "white",
        "gender": "men", "description": "Lightweight running shoes with air cushioning",
        "price": 8999, "rating": 4.5, "discount": 10, "stock": 50,
    },
    {
        "title": "Sony WH-1000XM4 Headphones",
        "brand": "sony", "category": "headphones", "color": "black",
        "gender": "unisex", "description": "Industry-leading noise cancelling wireless headphones",
        "price": 19990, "rating": 4.7, "discount": 15, "stock": 30,
    },
    {
        "title": "Samsung Galaxy M34 5G",
        "brand": "samsung", "category": "mobiles", "color": "blue",
        "gender": "unisex", "description": "6000mAh battery smartphone with 50MP camera",
        "price": 14999, "rating": 4.2, "discount": 12, "stock": 100,
    },
    {
        "title": "Puma RS-X Sneakers for Women",
        "brand": "puma", "category": "sneakers", "color": "pink",
        "gender": "women", "description": "Retro-inspired chunky sneakers for women",
        "price": 5499, "rating": 4.3, "discount": 25, "stock": 80,
    },
    {
        "title": "boAt Rockerz 450 Wireless Headphones",
        "brand": "boat", "category": "headphones", "color": "blue",
        "gender": "unisex", "description": "Over-ear wireless headphones with deep bass",
        "price": 1499, "rating": 4.0, "discount": 30, "stock": 150,
    },
    {
        "title": "Apple AirPods Pro 2nd Gen",
        "brand": "apple", "category": "earbuds", "color": "white",
        "gender": "unisex", "description": "Active noise cancellation wireless earbuds",
        "price": 20990, "rating": 4.8, "discount": 5, "stock": 40,
    },
    {
        "title": "Redmi Note 13 Pro",
        "brand": "redmi", "category": "mobiles", "color": "black",
        "gender": "unisex", "description": "200MP camera smartphone with AMOLED display",
        "price": 17999, "rating": 4.1, "discount": 8, "stock": 120,
    },
    {
        "title": "Nike Revolution 6 Running Shoes",
        "brand": "nike", "category": "shoes", "color": "red",
        "gender": "women", "description": "Cushioned running shoes for women",
        "price": 3295, "rating": 4.4, "discount": 20, "stock": 60,
    },
    {
        "title": "JBL Tune 760NC Headphones",
        "brand": "jbl", "category": "headphones", "color": "black",
        "gender": "unisex", "description": "Wireless over-ear noise cancelling headphones",
        "price": 3999, "rating": 4.3, "discount": 18, "stock": 90,
    }
]

async def seed_and_test():
    print("1. Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client[MONGO_DB]
    collection = db["products"]
    
    # Check if we already seeded to avoid duplicates
    count = await collection.count_documents({})
    if count == 0:
        print(f"2. Database is empty! Seeding {len(SAMPLE_PRODUCTS)} products to MongoDB and ES...")
        for product in SAMPLE_PRODUCTS:
            result = await collection.insert_one(product)
            mongo_id = str(result.inserted_id)
            # Index into ES as well
            await index_product(mongo_id, product, db)
            print(f"   -> Inserted & Indexed: {product['title']}")
    else:
        print(f"2. Database already has {count} products. Skipping seed.")

    print("\n3. Refreshing ES and Dynamic Registry...")
    es = Elasticsearch(ES_HOST)
    es.indices.refresh(index=ES_INDEX)
    force_refresh()

    print("\n4. Running Live Searches on the Database")
    queries = [
        "earbuds",
        "headphones",
        "mobiles above 15000",
        "earphons under 4k"
    ]

    for q in queries:
        print(f"\n--- Search: '{q}' ---")
        parsed = parse_query(q)
        vector = get_query_vector(parsed.keywords, q)
        results = search_products(parsed, vector)
        
        print(f"Parsed -> Brand: {parsed.brand}, Category: {parsed.category}, Price Max: {parsed.price_max}, Price Min: {parsed.price_min}")
        print(f"Found {len(results)} matches:")
        for r in results:
            print(f"   ✓ {r.get('title')} (Brand: {r.get('brand')}, Price: ₹{r.get('price')})")

if __name__ == "__main__":
    asyncio.run(seed_and_test())
