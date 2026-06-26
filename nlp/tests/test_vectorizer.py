"""
Smoke test for vectorizer.
Run: python -m nlp.tests.test_vectorizer
"""

from nlp.vectorizer import get_product_vector, get_query_vector

sample_product = {
    "title":       "boAt Rockerz 450 Wireless Headphones",
    "category":    "headphones",
    "description": "Over-ear wireless headphones with 15 hour battery and deep bass"
}

print("Testing product vectorizer...")
vec = get_product_vector(sample_product)
print(f"Product vector dims : {len(vec)}")   # should be 384
print(f"First 5 values      : {vec[:5]}")
print(f"Type                : {type(vec[0])}")

print("\nTesting query vectorizer...")
qvec = get_query_vector(["airpods", "wireless"], "airpods under 2k")
print(f"Query vector dims   : {len(qvec)}")  # should be 384
print(f"First 5 values      : {qvec[:5]}")

assert len(vec)  == 384, "Product vector must be 384 dims"
assert len(qvec) == 384, "Query vector must be 384 dims"
print("\nAll vectorizer tests passed.")
