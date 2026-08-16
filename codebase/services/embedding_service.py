from sentence_transformers import SentenceTransformer
from codebase.models import CodeChunk



MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text):
    embedding = model.encode(text)

    return embedding.tolist()

def generate_embeddings_for_chunks():
    chunks = CodeChunk.objects.filter(embedding__isnull=True)

    total = 0

    for chunk in chunks:
        chunk.embedding = generate_embedding(chunk.content)
        chunk.save(update_fields=["embedding"])
        total += 1

    return total