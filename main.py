from fastapi import FastAPI
import ollama
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

app = FastAPI()

client = chromadb.PersistentClient(path="./chroma_db")

ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",
)

collection = client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=ef,
)

# Rules go in the system message so the model treats them as instructions, not context
SYSTEM_PROMPT = """You answer questions using only the provided context.
Rules:
- Answer in one or two short sentences.
- Copy numbers exactly as they appear in the context. Do not calculate anything.
- Do not explain your reasoning.
- Do not add any information that is not in the context.
- If the answer is not in the context, reply exactly: I don't know based on the documents."""

# If even the closest chunk is farther than this, the documents don't cover the question.
# Picked from testing: answerable questions scored 0.181 to 0.294, out-of-scope 0.418 to 0.564.
RELEVANCE_THRESHOLD = 0.35
NO_ANSWER = "I don't know based on the documents."


@app.get("/ask")
def ask(question: str):
    # RETRIEVE the 3 most relevant chunks
    results = collection.query(query_texts=[question], n_results=3)
    distances = [round(d, 3) for d in results["distances"][0]]
    sources = [m["source"] for m in results["metadatas"][0]]

    # GUARDRAIL: skip the model entirely when nothing relevant was found
    if distances[0] > RELEVANCE_THRESHOLD:
        return {
            "question": question,
            "answer": NO_ANSWER,
            "answered_by": "relevance threshold",
            "sources": sources,
            "distances": distances,
            "context_used": [],
        }

    context = "\n\n".join(results["documents"][0])

    # AUGMENT: context first, question last, so the question is fresh when the model answers
    user_prompt = f"""Context:
{context}

Question: {question}
Answer:"""

    # GENERATE with temperature 0 so results are repeatable
    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0},
    )

    return {
        "question": question,
        "answer": response["message"]["content"],
        "answered_by": "model",
        "sources": sources,
        "distances": distances,
        "context_used": results["documents"][0],
    }