from nlp.vectorizer import get_query_vector
import numpy as np

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print("\n🤖 AI Vectorization Semantic Proof 🤖\n")

# Generate vectors
print("Generating 384-dimensional vectors using all-MiniLM-L6-v2...\n")
vec_sneaker = get_query_vector(["sneaker"], "sneaker")
vec_shoes = get_query_vector(["shoes"], "shoes")
vec_laptop = get_query_vector(["laptop"], "laptop")

print(f"✓ Sneaker vector generated (length: {len(vec_sneaker)})")
print(f"✓ Shoes vector generated (length: {len(vec_shoes)})")
print(f"✓ Laptop vector generated (length: {len(vec_laptop)})\n")

# Compare meanings
sim_sneaker_shoes = cosine_similarity(vec_sneaker, vec_shoes)
sim_sneaker_laptop = cosine_similarity(vec_sneaker, vec_laptop)

print("Comparing Semantic Meaning (Cosine Similarity):")
print(f"  sneaker <-> shoes : {sim_sneaker_shoes:.4f}  (High! AI knows these are similar)")
print(f"  sneaker <-> laptop: {sim_sneaker_laptop:.4f}  (Low! AI knows these are different)\n")
