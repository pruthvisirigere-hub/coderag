import math

from sentence_transformers import SentenceTransformer

# The same model your CodeRAG project uses
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "How do I download a repository from GitHub?",
    "Steps to clone a GitHub project",
    "Best pizza recipe for beginners",
]

# Each sentence becomes an "address": a list of numbers
addresses = [model.encode(s).tolist() for s in sentences]


def closeness(a, b):
    """Cosine similarity: 1.0 = same meaning, near 0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    length_a = math.sqrt(sum(x * x for x in a))
    length_b = math.sqrt(sum(y * y for y in b))
    return dot / (length_a * length_b)


print("How many numbers in one address:", len(addresses[0]))
print("First 5 numbers of sentence 1:  ", [round(n, 3) for n in addresses[0][:5]])
print()
print("Closeness of 1 and 2 (same meaning):", round(closeness(addresses[0], addresses[1]), 3))
print("Closeness of 1 and 3 (unrelated):   ", round(closeness(addresses[0], addresses[2]), 3))
print("Closeness of 2 and 3 (unrelated):   ", round(closeness(addresses[1], addresses[2]), 3))
