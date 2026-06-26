"""
End-to-end search test.
Requires: ES running + index created + products indexed.
Run: python -m nlp.tests.test_search
"""

from nlp.parser    import parse_query
from nlp.vectorizer import get_query_vector
from nlp.es_search  import search_products

queries = [
    "airpods under 2k",
    "boat headphones",
    "red nike shoes for women",
    "samsung mobile under 15000",
]

print("=" * 60)
print("END-TO-END SEARCH TEST")
print("(Requires ES running + products indexed)")
print("=" * 60)

for q in queries:
    print(f"\nQuery   : {q}")
    parsed  = parse_query(q)
    vector  = get_query_vector(parsed.keywords, q)
    results = search_products(parsed, vector)
    print(f"Parsed  : {parsed}")
    print(f"Results : {len(results)} products found")
    for i, r in enumerate(results[:3], 1):
        print(f"  #{i} {r.get('title','?')} — ₹{r.get('price','?')} — ★{r.get('rating','?')}")
