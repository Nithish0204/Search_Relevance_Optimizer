"""
Smoke test for parse_query().
Run: python -m nlp.tests.test_parser
"""

from nlp.parser import parse_query

tests = [
    # (input query, what you expect to see)
    ("airpods under 2k",                      "price_max=2000, keywords include airpods"),
    ("snekar for men below 1500",             "corrected sneaker, gender=men, price_max=1500"),
    ("boat headphones",                       "brand=boat, category=headphones"),
    ("red nike shoes for women above 500",    "color=red, brand=nike, gender=women, price_min=500"),
    ("iphon 15 pro",                          "corrected iphone, keywords include iphone"),
    ("samsung mobile between 10000 and 20000","brand=samsung, price range"),
    ("wireless earbuds under 3k",             "price_max=3000, category=earbuds"),
    ("laptop under 50000 for students",       "category=laptops, price_max=50000"),
    ("sony wh1000xm4",                        "brand=sony"),
    ("puma sneakers black",                   "brand=puma, color=black, category=sneakers"),
]

print("=" * 60)
print("PARSER SMOKE TEST")
print("=" * 60)
for query, note in tests:
    result = parse_query(query)
    print(f"\nInput   : {query}")
    print(f"Note    : {note}")
    print(f"keywords: {result.keywords}")
    print(f"price   : min={result.price_min}  max={result.price_max}")
    print(f"brand   : {result.brand}")
    print(f"color   : {result.color}")
    print(f"gender  : {result.gender}")
    print(f"category: {result.category}")
    print(f"corrected:{result.corrected_query}")
    print("-" * 40)
