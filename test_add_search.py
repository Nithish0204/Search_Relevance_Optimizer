import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from elasticsearch import Elasticsearch

from nlp.config import MONGO_URI, MONGO_DB, ES_HOST, ES_INDEX
from nlp.es_indexer import index_product
from nlp.parser import parse_query
from nlp.vectorizer import get_query_vector
from nlp.es_search import search_products
from nlp.registry import force_refresh

async def test_add_and_search():
    print("1. Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client[MONGO_DB]
    collection = db["products"]
    
    # Let's create a dummy product that doesn't exist yet
    new_product = {
        "title": "Quantum X9 Pro Gaming Mouse",
        "brand": "quantum",
        "category": "mouse",
        "color": "black",
        "gender": "unisex",
        "description": "High precision wireless RGB gaming mouse with 16000 DPI",
        "price": 2500,
        "rating": 4.8,
        "discount": 10,
        "stock": 50
    }
    
    print("2. Inserting product into MongoDB...")
    result = await collection.insert_one(new_product)
    mongo_id = str(result.inserted_id)
    print(f"   -> Inserted with ID: {mongo_id}")
    
    print("3. Indexing product into Elasticsearch (simulating FastAPI BackgroundTask)...")
    await index_product(mongo_id, new_product, db)
    
    print("4. Forcing ES refresh and updating dynamic registry...")
    es = Elasticsearch(ES_HOST)
    es.indices.refresh(index=ES_INDEX)
    force_refresh() # So the new brand "quantum" and category "mouse" get loaded
    
    print("\n5. Simulating a user search query...")
    user_query = "quantum gaming mouse under 3k"
    print(f"   Query: '{user_query}'")
    
    parsed = parse_query(user_query)
    print(f"   Parsed Entities:")
    print(f"      Brand:    {parsed.brand}")
    print(f"      Category: {parsed.category}")
    print(f"      Max Price:{parsed.price_max}")
    print(f"      Keywords: {parsed.keywords}")
    
    vector = get_query_vector(parsed.keywords, user_query)
    results = search_products(parsed, vector)
    
    print(f"\n6. Search Results ({len(results)} found):")
    for r in results:
        print(f"   - {r.get('title')} (Brand: {r.get('brand')}, Price: {r.get('price')})")
        
    print("\n7. Cleanup: Removing test product from MongoDB and ES...")
    await collection.delete_one({"_id": result.inserted_id})
    try:
        es.delete(index=ES_INDEX, id=mongo_id)
        es.indices.refresh(index=ES_INDEX)
        force_refresh()
    except Exception as e:
        print(f"   ES Cleanup skipped: {e}")
    print("   Done.")

if __name__ == "__main__":
    asyncio.run(test_add_and_search())
