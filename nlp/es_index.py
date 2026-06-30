"""
Create the Elasticsearch 'products' index.
Run this ONCE before indexing any products.

Usage:
    python -m nlp.es_index
"""

from elasticsearch import Elasticsearch
from nlp.config import ES_HOST, ES_INDEX

INDEX_CONFIG = {
    "settings": {
        "analysis": {
            "filter": {
                "product_synonyms": {
                    "type": "synonym",
                    "synonyms": [
                        # audio
                        "airpods, earphones, earbuds, tws, wireless earphones",
                        "headphones, headset, cans",
                        "speaker, bluetooth speaker, portable speaker",

                        # footwear
                        "shoes, sneakers, footwear, kicks",
                        "sandals, slippers, chappals, floaters",

                        # devices
                        "phone, smartphone, mobile, handset",
                        "laptop, notebook, computer",
                        "watch, smartwatch, wearable",
                        "tablet, ipad",

                        # accessories
                        "bag, backpack, sling bag, handbag",
                        "charger, adapter, power adapter",
                    ]
                },
                "english_stemmer": {
                    "type":     "stemmer",
                    "language": "english"
                }
            },
            "analyzer": {
                "product_analyzer": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stemmer",
                        "product_synonyms"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            # searchable text fields — use custom analyzer
            "title":       {"type": "text", "analyzer": "product_analyzer"},
            "category":    {
                "type": "text",
                "analyzer": "product_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {"type": "text", "analyzer": "product_analyzer"},

            # exact-match filter fields — keyword type
            "brand":       {"type": "keyword"},
            "color":       {"type": "keyword"},
            "gender":      {"type": "keyword"},
            "mongo_id":    {"type": "keyword"},

            # numeric fields for range filters and sorting
            "price":       {"type": "float"},
            "rating":      {"type": "float"},
            "discount":    {"type": "integer"},
            "stock":       {"type": "integer"},

            # 384-dim vector for semantic/kNN search
            "embedding": {
                "type":       "dense_vector",
                "dims":       384,
                "index":      True,
                "similarity": "cosine"
            }
        }
    }
}

def create_index():
    es = Elasticsearch(ES_HOST)

    if not es.ping():
        print(f"ERROR: Cannot connect to Elasticsearch at {ES_HOST}")
        print("Make sure ES is running: docker-compose up -d")
        return

    if es.indices.exists(index=ES_INDEX):
        print(f"Index '{ES_INDEX}' already exists. Skipping creation.")
        return

    es.indices.create(index=ES_INDEX, body=INDEX_CONFIG)
    print(f"Index '{ES_INDEX}' created successfully at {ES_HOST}")

if __name__ == "__main__":
    create_index()
