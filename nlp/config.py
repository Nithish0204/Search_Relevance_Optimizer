import os
from dotenv import load_dotenv

load_dotenv()

# Elasticsearch
ES_HOST  = os.getenv("ES_HOST",  "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "products")

# MongoDB (used only by bulk_index.py)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "search_optimizer")

# Sentence Transformer
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
