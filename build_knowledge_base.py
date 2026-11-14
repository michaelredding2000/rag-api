import os
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

DOCS_DIR = "docs"


def table_to_sentences(table_lines):
    """Turn markdown table rows into plain sentences the model can read."""
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in table_lines]
    header = rows[0]
    sentences = []
    for row in rows[1:]:
        if all(set(cell) <= set("-: ") for cell in row):
            continue  # skip the |---|---| separator line
        parts = [f"{h} is {v}" for h, v in zip(header, row)]
        sentences.append("Row: " + ", ".join(parts) + ".")
    return "\n".join(sentences)


def convert_tables(section):
    """Find markdown tables inside a section and replace them with sentences."""
    output, table = [], []
    for line in section.splitlines():
        if line.strip().startswith("|"):
            table.append(line)
        else:
            if table:
                output.append(table_to_sentences(table))
                table = []
            output.append(line)
    if table:
        output.append(table_to_sentences(table))
    return "\n".join(output).replace("**", "")  # also strip bold markers


def chunk_markdown(text):
    """Split a markdown file into sections, keeping each heading with its content."""
    sections, current = [], []
    for line in text.splitlines():
        if line.strip() == "---":
            continue
        if line.startswith("#") and current:
            sections.append("\n".join(current).strip())
            current = []
        current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [convert_tables(s) for s in sections if s]


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
        chunks.append(f"[Source: {source}]\n{piece}")
        ids.append(f"{source}_{i}")
        metadatas.append({"source": source, "chunk_index": i})

    print(f"{filename}: {len(pieces)} chunks")

# Save a preview of every chunk so you can check what the model will see
with open("chunks_preview.txt", "w", encoding="utf-8") as f:
    f.write("\n\n==========\n\n".join(chunks))

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