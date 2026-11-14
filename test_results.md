\# RAG API Test Results



Model: qwen2.5:0.5b | Embeddings: nomic-embed-text | Chunks retrieved per question: 2



\## Test 1

Question: What is my career goal?

Expected: Junior AI engineer or prompt engineer at a federal contractor in the DC area

Right chunk retrieved: Yes (career goal paragraph was the top match)

Answer correct: Mostly

Made-up details: Said a federal contractor is "likely a government agency" (wrong, contractors are private companies). Added a goal of moving to a senior position, which is not in the profile.

Notes: Second retrieved chunk (citizenship) was not relevant. The search always returns 2 chunks, so it grabs the next closest one.



\## Test 2

Question: What tools and languages do I know?

Expected: Python, SQL, Power BI, Tableau, Excel

Right chunk retrieved: Yes, but ranked second. The career goal paragraph ranked first even though it does not answer the question.

Answer correct: Mostly. All five tools listed correctly.

Made-up details: Listed NextWork as a tool, and called it "a powerful project management and collaboration tool" (wrong, it is a learning platform). Ended with an unrelated sentence: "You are an AI assistant that helps you know more and find answers to your queries."

Notes: The model added information beyond the context both times so far. Pattern: grounds the core fact, then pads.



\## Test 3

Question: What is my favorite food?

Expected: The context does not say

Right chunk retrieved: N/A. Nothing in the profile covers this, but ChromaDB still returned 2 chunks (citizenship and name) because it always returns its closest matches.

Answer correct: Yes. It said the context has no information about my favorite food.

Made-up details: None

Notes: The prompt instruction "If the context doesn't contain relevant information, say so" kept the model from inventing an answer.



\## Summary so far

3 tests: 1 fully correct (correctly refused), 2 mostly correct with made-up details added.

Pattern: retrieval finds the right chunk, the model grounds the core fact, then adds details that aren't in the context.

