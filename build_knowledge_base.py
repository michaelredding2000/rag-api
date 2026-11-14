import os
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

DOCS_DIR = "docs"


def chunk_markdown(text):
    """Split a markdown file into sections, keeping each heading with its content."""
    sections, current = [], []
    for line in text.splitlines():
        if line.strip() == "---":
            continue  # skip horizontal divider lines
        if line.startswith("#") and current:
            sections.append("\n".join(current).strip())
            current = []
        current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [s for s in sections if s]


def chunk_text(text):
    """Split a plain text file into paragraphs at blank lines."""
    return [c.strip() for c in text.split("\n\n") if c.strip()]


chunks, ids, metadatas = [], [], []

for filename in sorted(os.listdir(DOCS_DIR)):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    source = os.path.splitext(filename)[0]
    pieces = chunk_markdown(text) if filename.endswith(".md") else chunk_text(text)

    for i, piece in enumerate(pieces):
        chunks.append(f"[Source: {source}]\n{piece}")  # label helps retrieval and answers
        ids.append(f"{source}_{i}")
        metadatas.append({"source": source, "chunk_index": i})

    print(f"{filename}: {len(pieces)} chunks")

client = chromadb.PersistentClient(path="./chroma_db")

ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",
)

collection = client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=ef,
)

collection.add(ids=ids, documents=chunks, metadatas=metadatas)

print(f"Added {len(chunks)} chunks to the 'knowledge_base' collection.")
print("Knowledge base built successfully!")