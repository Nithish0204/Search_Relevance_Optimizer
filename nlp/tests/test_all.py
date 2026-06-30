"""
Comprehensive NLP + Elasticsearch test suite.
Tests every module in the nlp/ folder in one run.

IMPORTANT: Since the NLP pipeline is now fully dynamic (loads brands,
colors, categories from ES), we MUST seed sample products into a test
ES index BEFORE running entity extraction tests.

Run:  python -m nlp.tests.test_all

Sections:
    1. Normalizer    — shorthand expansion, gender normalization
    2. ES Setup      — create test index + seed sample products
    3. Registry      — dynamic data loading from ES
    4. Spell checker — correction + dynamically protected words
    5. Entities      — price, brand, color, gender, category, keywords
    6. Parser        — full pipeline (normalize → spell → extract)
    7. Vectorizer    — embedding dimensions + consistency
    8. ES Search     — hybrid BM25 + kNN search via manual RRF
    9. Cleanup
"""

import sys
import time

# ── tracking ──────────────────────────────────────────────────────
passed  = 0
failed  = 0
errors  = []

def check(test_name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {test_name}")
    else:
        failed += 1
        msg = f"  ❌ {test_name}"
        if detail:
            msg += f"  →  {detail}"
        print(msg)
        errors.append(test_name)

def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ══════════════════════════════════════════════════════════════════
#  1. NORMALIZER (no ES needed — pure regex)
# ══════════════════════════════════════════════════════════════════
section("1. NORMALIZER")
from nlp.normalizer import normalize

check("2k → 2000",           normalize("2k") == "2000")
check("15k → 15000",         normalize("15k") == "15000")
check("mens → men",          normalize("mens") == "men")
check("womens → women",      normalize("womens") == "women")
check("ladies → women",      normalize("ladies") == "women")
check("gents → men",         normalize("gents") == "men")
check("lappy → laptop",      normalize("lappy") == "laptop")
check("phn → phone",         normalize("phn") == "phone")
check("tws → earbuds",       normalize("tws") == "earbuds")
check("snekar → sneaker",    normalize("snekar") == "sneaker")
check("rs removed",          normalize("rs 500") == "500")
check("rupees removed",      normalize("rupees 1000") == "1000")
check("mixed: under 2k",     normalize("under 2k") == "under 2000")
check("mixed: lappy under 50k", normalize("lappy under 50k") == "laptop under 50000")

# ══════════════════════════════════════════════════════════════════
#  2. ES SETUP — create test index + seed products
#     (must happen BEFORE entity/spell/parser tests since they
#      dynamically load brands/colors/categories from ES)
# ══════════════════════════════════════════════════════════════════
section("2. ES SETUP (seed test data)")

from elasticsearch import Elasticsearch
from nlp.config import ES_HOST, ES_INDEX
from nlp.vectorizer import get_product_vector

TEST_INDEX = "test_products_nlp"
es = Elasticsearch(ES_HOST)

es_available = False
try:
    es_available = es.ping()
except Exception:
    pass

if not es_available:
    print("\n  ⚠️  Elasticsearch is NOT reachable at", ES_HOST)
    print("  ⚠️  Skipping ES-dependent tests.")
    print("  ⚠️  Start ES and re-run to test full pipeline.\n")
else:
    print(f"  ✓ Elasticsearch is reachable at {ES_HOST}\n")

    from nlp.es_index import INDEX_CONFIG

    # cleanup old test index if exists
    try:
        if es.indices.exists(index=TEST_INDEX):
            es.indices.delete(index=TEST_INDEX)
    except Exception:
        pass

    # create test index
    try:
        es.indices.create(index=TEST_INDEX, body=INDEX_CONFIG)
        check("test index created", es.indices.exists(index=TEST_INDEX))
    except Exception as e:
        check(f"test index created (ERROR: {e})", False)

    # seed sample products
    SAMPLE_PRODUCTS = [
        {
            "title": "boAt Airdopes 141 True Wireless",
            "brand": "boat", "category": "earbuds", "color": "black",
            "gender": "", "description": "Bluetooth wireless earbuds with 42H playtime",
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
            "gender": "", "description": "Industry-leading noise cancelling wireless headphones",
            "price": 19990, "rating": 4.7, "discount": 15, "stock": 30,
        },
        {
            "title": "Samsung Galaxy M34 5G",
            "brand": "samsung", "category": "mobiles", "color": "blue",
            "gender": "", "description": "6000mAh battery smartphone with 50MP camera",
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
            "gender": "", "description": "Over-ear wireless headphones with deep bass",
            "price": 1499, "rating": 4.0, "discount": 30, "stock": 150,
        },
        {
            "title": "Apple AirPods Pro 2nd Gen",
            "brand": "apple", "category": "earbuds", "color": "white",
            "gender": "", "description": "Active noise cancellation wireless earbuds",
            "price": 20990, "rating": 4.8, "discount": 5, "stock": 40,
        },
        {
            "title": "Redmi Note 13 Pro",
            "brand": "redmi", "category": "mobiles", "color": "black",
            "gender": "", "description": "200MP camera smartphone with AMOLED display",
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
            "gender": "", "description": "Wireless over-ear noise cancelling headphones",
            "price": 3999, "rating": 4.3, "discount": 18, "stock": 90,
        },
    ]

    indexed_count = 0
    try:
        for i, product in enumerate(SAMPLE_PRODUCTS):
            embedding = get_product_vector(product)
            doc = {**product, "embedding": embedding, "mongo_id": f"test_{i}"}
            es.index(index=TEST_INDEX, id=f"test_{i}", document=doc)
            indexed_count += 1

        es.indices.refresh(index=TEST_INDEX)
        count = es.count(index=TEST_INDEX)["count"]
        check(f"indexed {indexed_count}/10 products", indexed_count == 10)
        check(f"ES doc count = {count}", count == 10)
    except Exception as e:
        check(f"product indexing (ERROR: {e})", False)

    # ══════════════════════════════════════════════════════════════
    #  3. REGISTRY — dynamic data loading
    # ══════════════════════════════════════════════════════════════
    section("3. REGISTRY (dynamic data loading)")
    import nlp.registry as registry
    import nlp.config as cfg
    import nlp.es_search as es_search_mod

    # point registry to test index
    original_index = cfg.ES_INDEX
    cfg.ES_INDEX = TEST_INDEX
    registry.ES_INDEX = TEST_INDEX
    es_search_mod.ES_INDEX = TEST_INDEX

    # force refresh from test index
    registry.force_refresh()

    brands     = registry.get_brands()
    colors     = registry.get_colors()
    categories = registry.get_categories()

    check("brands loaded from ES",     len(brands) > 0, f"got {brands}")
    check("colors loaded from ES",     len(colors) > 0, f"got {colors}")
    check("categories loaded from ES", len(categories) > 0, f"got {categories}")

    check("'boat' in brands",    "boat" in brands,    f"brands: {brands}")
    check("'nike' in brands",    "nike" in brands,    f"brands: {brands}")
    check("'samsung' in brands", "samsung" in brands, f"brands: {brands}")
    check("'black' in colors",   "black" in colors,   f"colors: {colors}")
    check("'headphones' in categories", "headphones" in categories,
          f"categories: {categories}")

    # ══════════════════════════════════════════════════════════════
    #  4. SPELL CHECKER (uses dynamic protected words)
    # ══════════════════════════════════════════════════════════════
    section("4. SPELL CHECKER (dynamic)")
    from nlp.spell import correct_spelling

    check("boat protected (from ES brands)",
          correct_spelling("boat") == "boat")
    check("nike protected (from ES brands)",
          correct_spelling("nike") == "nike")
    check("digits preserved",
          correct_spelling("1500") == "1500")
    check("correct word unchanged",
          correct_spelling("headphones") == "headphones")
    corrected = correct_spelling("sneaker for men")
    check("'sneaker for men' stays",
          "sneaker" in corrected and "men" in corrected)

    # ══════════════════════════════════════════════════════════════
    #  5. ENTITY EXTRACTION (uses dynamic data)
    # ══════════════════════════════════════════════════════════════
    section("5. ENTITY EXTRACTION (dynamic)")
    from nlp.entities import (
        extract_price, extract_brand, extract_color,
        extract_gender, extract_category, extract_keywords,
    )

    # ── Price (regex-based, no ES needed) ──
    section("5a. Price Extraction")
    check("under 2000",           extract_price("under 2000") == (None, 2000.0))
    check("below 1500",           extract_price("below 1500") == (None, 1500.0))
    check("less than 3000",       extract_price("less than 3000") == (None, 3000.0))
    check("above 500",            extract_price("above 500") == (500.0, None))
    check("more than 1000",       extract_price("more than 1000") == (1000.0, None))
    p = extract_price("between 500 and 2000")
    check("between 500 and 2000", p == (500.0, 2000.0), f"got {p}")
    p = extract_price("500 to 2000")
    check("500 to 2000",          p == (500.0, 2000.0), f"got {p}")
    p = extract_price("around 1500")
    check("around 1500 (±20%)",   p == (1200.0, 1800.0), f"got {p}")
    check("no price",             extract_price("nike shoes") == (None, None))

    # ── Brand (dynamic from ES) ──
    section("5b. Brand Extraction (dynamic)")
    check("boat detected",    extract_brand("boat earphones") == "boat")
    check("nike detected",    extract_brand("nike shoes") == "nike")
    check("samsung detected", extract_brand("samsung mobile") == "samsung")
    check("sony detected",    extract_brand("sony headphones") == "sony")
    check("puma detected",    extract_brand("puma sneakers") == "puma")
    check("no brand",         extract_brand("wireless earbuds") is None)

    # ── Color (dynamic from ES) ──
    section("5c. Color Extraction (dynamic)")
    check("red detected",    extract_color("red shoes") == "red")
    check("black detected",  extract_color("black headphones") == "black")
    check("no color",        extract_color("wireless earbuds") is None)

    # ── Gender (regex-based, universal) ──
    section("5d. Gender Extraction")
    check("for men",          extract_gender("shoes for men") == "men")
    check("for women",        extract_gender("bag for women") == "women")
    check("unisex",           extract_gender("unisex watch") == "unisex")
    check("men standalone",   extract_gender("men shoes") == "men")
    check("no gender",        extract_gender("laptop") is None)

    # ── Category (dynamic from ES) ──
    section("5e. Category Extraction (dynamic)")
    check("headphones",  extract_category("wireless headphones") == "headphones")
    check("shoes",       extract_category("running shoes") == "shoes")
    check("sneakers",    extract_category("sneaker for men") == "sneakers")
    check("earbuds",     extract_category("earbuds under 1000") == "earbuds")
    check("mobiles",     extract_category("samsung mobile") == "mobiles")

    # ── Keywords ──
    section("5f. Keyword Extraction")
    kw = extract_keywords("wireless headphones")
    check("keywords: wireless headphones",
          "wireless" in kw or "headphones" in kw, f"got {kw}")
    kw = extract_keywords("sony wh1000xm4")
    check("keywords: sony wh1000xm4",
          "sony" in kw or "wh1000xm4" in kw, f"got {kw}")
    check("max 6 keywords",
          len(extract_keywords("a b c d e f g h i j")) <= 6)

    # ══════════════════════════════════════════════════════════════
    #  6. PARSER (full pipeline, dynamic)
    # ══════════════════════════════════════════════════════════════
    section("6. PARSER (full pipeline, dynamic)")
    from nlp.parser import parse_query
    from nlp.models import ParsedQuery

    r = parse_query("airpods under 2k")
    check("airpods under 2k → price_max=2000",    r.price_max == 2000.0)
    check("airpods under 2k → has keywords",       len(r.keywords) > 0)
    check("airpods under 2k → returns ParsedQuery", isinstance(r, ParsedQuery))

    r = parse_query("sneaker for men below 1500")
    check("sneaker → gender=men",                  r.gender == "men")
    check("sneaker → price_max=1500",              r.price_max == 1500.0)

    r = parse_query("boat headphones")
    check("boat headphones → brand=boat",          r.brand == "boat")
    check("boat headphones → category=headphones", r.category == "headphones")

    r = parse_query("red nike shoes for women above 500")
    check("complex → color=red",                   r.color == "red")
    check("complex → brand=nike",                  r.brand == "nike")
    check("complex → gender=women",                r.gender == "women")
    check("complex → price_min=500",               r.price_min == 500.0)
    check("complex → category=shoes",              r.category == "shoes")

    r = parse_query("samsung mobile between 10000 and 20000")
    check("range → brand=samsung",                 r.brand == "samsung")
    check("range → price_min=10000",               r.price_min == 10000.0)
    check("range → price_max=20000",               r.price_max == 20000.0)
    check("range → category=mobiles",              r.category == "mobiles")

    r = parse_query("wireless earbuds under 3k")
    check("3k → price_max=3000",                   r.price_max == 3000.0)

    r = parse_query("puma sneakers black")
    check("puma sneakers → brand=puma",            r.brand == "puma")
    check("puma sneakers → color=black",           r.color == "black")
    check("puma sneakers → category=sneakers",     r.category == "sneakers")

    # edge cases
    r = parse_query("")
    check("empty query → no crash",                isinstance(r, ParsedQuery))
    r = parse_query("asdfghjkl")
    check("gibberish → no crash",                  isinstance(r, ParsedQuery))

    # ══════════════════════════════════════════════════════════════
    #  7. VECTORIZER
    # ══════════════════════════════════════════════════════════════
    section("7. VECTORIZER")
    from nlp.vectorizer import get_query_vector

    sample_product = {
        "title":       "boAt Rockerz 450 Wireless Headphones",
        "category":    "headphones",
        "description": "Over-ear wireless headphones with 15 hour battery"
    }
    pvec = get_product_vector(sample_product)
    check("product vector is list",       isinstance(pvec, list))
    check("product vector dims = 384",    len(pvec) == 384)
    check("product vector has floats",    isinstance(pvec[0], float))

    qvec = get_query_vector(["airpods", "wireless"], "airpods under 2k")
    check("query vector dims = 384",      len(qvec) == 384)
    check("query vector has floats",      isinstance(qvec[0], float))

    qvec2 = get_query_vector(["airpods", "wireless"], "airpods under 2k")
    check("vectorizer is deterministic",  qvec == qvec2)

    qvec3 = get_query_vector([], "airpods under 2k")
    check("empty keywords → uses raw query", len(qvec3) == 384)

    qvec4 = get_query_vector(["laptop", "gaming"], "gaming laptop")
    check("different input → different vector", qvec4 != qvec)

    # ══════════════════════════════════════════════════════════════
    #  8. ES HYBRID SEARCH
    # ══════════════════════════════════════════════════════════════
    section("8. ES HYBRID SEARCH")
    from nlp.es_search import (
        _build_bm25_query, _build_knn_query,
        _reciprocal_rank_fusion, search_products,
    )

    try:
        # ── Test: airpods under 2k ──
        parsed = parse_query("airpods under 2k")
        vector = get_query_vector(parsed.keywords, "airpods under 2k")
        results = search_products(parsed, vector)
        check("'airpods under 2k' returns results",  len(results) > 0)
        if results:
            check("results have price ≤ 2000",
                  all(r.get("price", 99999) <= 2000 for r in results),
                  f"prices: {[r.get('price') for r in results]}")

        # ── Test: boat headphones ──
        parsed = parse_query("boat headphones")
        vector = get_query_vector(parsed.keywords, "boat headphones")
        results = search_products(parsed, vector)
        check("'boat headphones' returns results",    len(results) > 0)
        if results:
            brands_found = [r.get("brand", "") for r in results]
            check("boat in results", "boat" in brands_found,
                  f"brands: {brands_found}")

        # ── Test: nike shoes for women ──
        parsed = parse_query("red nike shoes for women")
        vector = get_query_vector(parsed.keywords, "red nike shoes for women")
        results = search_products(parsed, vector)
        check("'red nike shoes for women' returns results", len(results) > 0)

        # ── Test: samsung mobile under 15000 ──
        parsed = parse_query("samsung mobile under 15000")
        vector = get_query_vector(parsed.keywords, "samsung mobile under 15000")
        results = search_products(parsed, vector)
        check("'samsung mobile under 15000' returns results", len(results) > 0)
        if results:
            check("results have price ≤ 15000",
                  all(r.get("price", 99999) <= 15000 for r in results),
                  f"prices: {[r.get('price') for r in results]}")

        # ── Test: sony headphones ──
        parsed = parse_query("sony headphones")
        vector = get_query_vector(parsed.keywords, "sony headphones")
        results = search_products(parsed, vector)
        check("'sony headphones' returns results",    len(results) > 0)

        # ── Test: RRF merges correctly ──
        parsed = parse_query("wireless earbuds")
        vector = get_query_vector(parsed.keywords, "wireless earbuds")
        bm25_q = _build_bm25_query(parsed)
        knn_q  = _build_knn_query(parsed, vector)
        bm25_r = es.search(index=TEST_INDEX, body=bm25_q)
        knn_r  = es.search(index=TEST_INDEX, body=knn_q)
        bm25_hits = bm25_r["hits"]["hits"]
        knn_hits  = knn_r["hits"]["hits"]
        fused = _reciprocal_rank_fusion(bm25_hits, knn_hits)
        check("BM25 returns hits",          len(bm25_hits) > 0)
        check("kNN returns hits",           len(knn_hits) > 0)
        check("RRF fusion returns results", len(fused) > 0)
        check("RRF result is list of dicts",
              all(isinstance(r, dict) for r in fused))

    except Exception as e:
        check(f"search tests (ERROR: {e})", False)

    # ══════════════════════════════════════════════════════════════
    #  9. CLEANUP
    # ══════════════════════════════════════════════════════════════
    section("9. CLEANUP")
    try:
        cfg.ES_INDEX = original_index
        registry.ES_INDEX = original_index
        es_search_mod.ES_INDEX = original_index
        es.indices.delete(index=TEST_INDEX)
        check("test index cleaned up", not es.indices.exists(index=TEST_INDEX))
    except Exception as e:
        check(f"cleanup (ERROR: {e})", False)

# ══════════════════════════════════════════════════════════════════
#  FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════
section("FINAL SUMMARY")
total = passed + failed
print(f"\n  Total : {total} tests")
print(f"  Passed: {passed} ✅")
print(f"  Failed: {failed} ❌")

if errors:
    print(f"\n  Failed tests:")
    for e in errors:
        print(f"    • {e}")

print()
if failed == 0:
    print("  🎉 ALL TESTS PASSED!")
else:
    print(f"  ⚠️  {failed} test(s) failed — review above.")

print()
sys.exit(0 if failed == 0 else 1)
