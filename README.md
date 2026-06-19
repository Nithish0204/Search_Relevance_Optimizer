# Search Relevance Optimizer

> AI-powered e-commerce search engine with hybrid BM25 + semantic search, NLP query parsing, and business signal ranking.

Inspired by how Amazon and Flipkart handle natural language queries like *"airpods under 2k"* — returning the right products even when the user misspells, uses synonyms, or mixes filters into plain English.

---

## What it does

- Understands natural language queries: `"snekar for men below 1500"` → finds sneakers, male, price ≤ ₹1500
- Corrects spelling automatically: `"airpodds"` → `"airpods"`
- Handles synonyms: `"earphones"` finds products tagged as `earbuds`, `tws`, `wireless earphones`
- Fuzzy matches brand names: `"nkie"` still finds Nike
- Combines keyword relevance (BM25) + semantic meaning (cosine similarity) into one hybrid score
- Boosts products with higher ratings, bigger discounts, and in-stock status

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React.js | Search UI, product cards, admin panel |
| Backend | FastAPI (Python) | API routes, validation, orchestration |
| Primary DB | MongoDB | Source of truth for all product data |
| Search Engine | Elasticsearch 8.x | Inverted index + dense vector (HNSW) |
| NLP | spaCy + SymSpell | Spell correction, entity extraction |
| ML Model | all-MiniLM-L6-v2 | 384-dim text embeddings (Sentence Transformers) |
| Fuzzy Match | RapidFuzz | Brand name matching with edit distance |
| Hybrid Merge | ES RRF (built-in) | Reciprocal Rank Fusion of BM25 + cosine |

---

## Project Structure

```
search-relevance-optimizer/
├── backend/
│   ├── main.py                  # FastAPI app, startup, routes
│   ├── config.py                # .env config via pydantic_settings
│   ├── models.py                # Product, ParsedQuery Pydantic models
│   ├── nlp/
│   │   ├── parser.py            # parse_query(raw) → ParsedQuery  ← YOUR FILE
│   │   ├── spell.py             # SymSpell wrapper
│   │   └── entities.py          # price/brand/color/gender extractors
│   ├── search/
│   │   ├── es_client.py         # search_products(parsed, vector)  ← YOUR FILE
│   │   ├── indexer.py           # index_product(id, product, emb)  ← YOUR FILE
│   │   └── query_builder.py     # build_es_query(parsed, vector) → dict
│   └── db/
│       └── mongo.py             # async MongoDB client
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── SearchBar.jsx
│       │   ├── ProductCard.jsx
│       │   └── FilterPanel.jsx
│       └── api/
│           └── search.js        # axios calls to FastAPI
├── scripts/
│   └── bulk_index.py            # one-time script to index all MongoDB products into ES
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## Team Roles

| Person | Owns | Key files |
|---|---|---|
| You (NLP/ML + ES) | Query parsing, ES setup, embedding, search logic | `nlp/parser.py`, `search/es_client.py`, `search/indexer.py` |
| Backend dev | FastAPI routes, MongoDB CRUD, response shaping | `main.py`, `db/mongo.py` |
| Frontend dev | React UI, search bar, product cards, filters | `frontend/src/` |

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for Elasticsearch and MongoDB)

### 1. Clone and install

```bash
git clone https://github.com/yourteam/search-relevance-optimizer.git
cd search-relevance-optimizer
```

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn motor elasticsearch sentence-transformers spacy symspellpy rapidfuzz pydantic-settings
python -m spacy download en_core_web_sm
```

```bash
# Frontend
cd frontend
npm install
```

### 2. Start services

```bash
# Start Elasticsearch and MongoDB via Docker
docker-compose up -d
```

Verify ES is running: open `http://localhost:9200` — you should see a JSON response.

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
ES_HOST=http://localhost:9200
MONGO_URI=mongodb://localhost:27017
ES_INDEX=products
MODEL_NAME=all-MiniLM-L6-v2
CACHE_TTL=300
```

### 4. Create the Elasticsearch index

```bash
cd backend
python scripts/create_index.py
```

This creates the `products` index with the synonym filter, stemmer, and dense_vector mapping. **Run this once before indexing any products.**

### 5. Run the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 6. Run the frontend

```bash
cd frontend
npm start
```

App: `http://localhost:3000`

### 7. Seed sample data (optional)

```bash
cd backend
python scripts/seed_products.py       # adds 50 sample products to MongoDB
python scripts/bulk_index.py          # indexes all MongoDB products into ES
```

---

## API Endpoints

### Search

```
GET /search?q=airpods+under+2k
```

Response:
```json
{
  "results": [
    {
      "title": "boAt Airdopes 141 True Wireless",
      "brand": "boAt",
      "category": "earbuds",
      "price": 1299,
      "rating": 4.1,
      "discount": 20,
      "stock": 200
    }
  ],
  "total": 8,
  "corrected_query": null
}
```

### Add product (admin)

```
POST /products
Content-Type: application/json

{
  "title": "Sony WH-1000XM4",
  "brand": "Sony",
  "category": "headphones",
  "price": 19990,
  "rating": 4.7,
  "discount": 15,
  "stock": 50,
  "description": "Industry-leading noise cancelling wireless headphones..."
}
```

Response:
```json
{ "id": "64abc123...", "status": "saved" }
```

---

## Architecture: Key Design Decisions

### MongoDB first, Elasticsearch second

MongoDB is the source of truth. Elasticsearch is a search index built on top of it. When ES goes down, products are still safe in MongoDB. A fallback text search on MongoDB kicks in automatically.

### Async ES indexing

Writing to ES takes 50–200ms due to embedding generation. This happens in a FastAPI `BackgroundTask` — the admin gets an instant response, and ES indexing happens after. If it fails, it's logged to `sync_failures` for retry.

### Synonyms live in ES, not in the NLP parser

The ES analyzer handles synonym expansion at both index time and query time. The NLP parser only does spell correction, normalization, and entity extraction. Doing synonyms in both places causes double expansion.

### One ES request, not two

Both BM25 keyword search and kNN vector search run inside a single ES request. ES merges them using built-in Reciprocal Rank Fusion (RRF). No manual score normalization needed.

### RRF merges BM25 and vector scores

BM25 scores are unbounded (0 to ∞). Cosine similarity is 0–1. You cannot add them directly. RRF converts both to rank-based scores and merges them correctly.

---

## The Search Flow (plaintext summary)

```
User types: "snekar for men below 1500"
        ↓
React sends GET /search?q=snekar+for+men+below+1500
        ↓
FastAPI checks cache → miss
        ↓
NLP parser:
  1. lowercase + clean   → "snekar for men below 1500"
  2. spell correction    → "sneaker for men below 1500"
  3. normalization       → no change needed
  4. entity extraction   → gender=men, price_max=1500, keywords=["sneaker"]
        ↓
Sentence Transformer encodes "sneaker" → [0.12, -0.34, ...] (384 dims)
        ↓
Elasticsearch receives one request with:
  - multi_match "sneaker" on title^3, category^2, description^1
    (ES synonym filter also matches: shoes, footwear, kicks)
  - kNN cosine search on embedding field
  - filter: price ≤ 1500, gender = men
  - rank: rrf {}
        ↓
ES returns ranked products → script_score boosts high-rating / discounted items
        ↓
FastAPI caches result, returns JSON with corrected_query="sneaker for men below 1500"
        ↓
React shows: "Did you mean: sneaker?" + product cards ranked by relevance
```

---

## Interface Contract (agree with team on Day 1)

```python
# You give the backend dev these two functions:

from nlp.parser import parse_query
parsed = parse_query("airpods under 2k")
# → ParsedQuery(keywords=['airpods'], price_max=2000, brand=None, gender=None, ...)

from search.es_client import search_products
results = search_products(parsed, query_vector)
# → [{"title": "...", "price": 999, "rating": 4.2, ...}, ...]
```

---

## Bonus Features (add after core works)

- [ ] Autocomplete suggestions (ES completion suggester)
- [ ] Search analytics logging (MongoDB search_logs collection)
- [ ] Popular searches widget (aggregate from logs)
- [ ] Click tracking to improve ranking
- [ ] Admin dashboard to see sync_failures and retry

---

## Resume Line

> "Built a hybrid e-commerce search engine with Elasticsearch BM25 + Sentence-BERT semantic search, Reciprocal Rank Fusion, NLP query parsing (spaCy + SymSpell), and async embedding generation — enabling Amazon-style natural language product discovery with sub-100ms cached response."

---

*Built for VRSEC group project | Inspired by Amazon, Flipkart, Nykaa, Meesho*
