import sys

from chunker import chunk_file  # Piece 3: cuts files into chunks
from mini_loader import load_files  # Piece 1: finds and reads the files

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_model():
    # Imported here so this file can be tested without the big library
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)  # loaded ONCE, then reused


def build_embedding_text(chunk):
    """The text we embed: where the code lives + its name + the code itself."""
    lines = [f"File: {chunk['file_path']}"]

    if chunk["name"]:
        lines.append(f"Name: {chunk['name']} ({chunk['type']})")

    lines.append("")
    lines.append(chunk["content"])
    return "\n".join(lines)


def embed_chunks(model, chunks, batch_size=32):
    """Adds 'embedding', 'tokens' and 'truncated' to every chunk."""
    if not chunks:
        return chunks  # nothing to embed

    texts = [build_embedding_text(c) for c in chunks]

    # How many word-pieces each text has, versus what the model can read
    limit = model.max_seq_length
    token_counts = [
        len(ids) for ids in model.tokenizer(texts, truncation=False)["input_ids"]
    ]

    # One call for ALL texts; the library cuts them into batches internally
    vectors = model.encode(texts, batch_size=batch_size, show_progress_bar=False)

    for chunk, count, vector in zip(chunks, token_counts, vectors):
        chunk["embedding"] = [float(x) for x in vector]
        chunk["tokens"] = count
        chunk["truncated"] = count > limit

    return chunks


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python embedder.py <folder>")
        sys.exit(1)

    files, _ = load_files(sys.argv[1])

    chunks = []
    for f in files:
        chunks.extend(chunk_file(f))

    if not chunks:
        print("No chunks found, so nothing to embed.")
        sys.exit(0)

    model = load_model()
    embed_chunks(model, chunks)

    truncated = [c for c in chunks if c["truncated"]]

    print(f"Chunks embedded: {len(chunks)}")
    print(f"Numbers per embedding: {len(chunks[0]['embedding'])}")
    print(f"Model reads at most {model.max_seq_length} word-pieces per chunk")
    print(f"Chunks too long (end gets cut off): {len(truncated)} of {len(chunks)}")

    if truncated:
        print()
        print("Longest chunks:")
        for c in sorted(truncated, key=lambda c: c["tokens"], reverse=True)[:5]:
            print(
                f"  {c['tokens']:>5} word-pieces  {c['file_path']}  "
                f"[{c['type']}: {c['name']}]"
            )
