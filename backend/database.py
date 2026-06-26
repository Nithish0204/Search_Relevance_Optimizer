import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env from the parent directory (project root)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, ".env"))

# Use tlsAllowInvalidCertificates=True so MacOS doesn't complain about Atlas SSL certs locally
client = MongoClient(os.getenv("MONGO_URI"), tlsAllowInvalidCertificates=True)
db_name = os.getenv("MONGO_DB", "search_optimizer")
db = client[db_name]
products_collection = db["products"]