# RAG API: Testing How Accurately a Local AI Answers Questions From My Reports

A question-answering API that searches my own analysis reports and answers from them using a local language model. I built the base from NextWork's RAG API project, then swapped in my own documents, wrote a test set with known answers, and ran six rounds of experiments to measure and improve accuracy.

**Result: accuracy went from 3 to 9 out of 10, and the API stopped making up answers to questions the documents don't cover.**

## How it works

1. **Retrieve:** the question is converted into an embedding, and ChromaDB finds the 3 most similar chunks from my documents
2. **Guardrail:** if even the closest chunk is too far from the question, the API answers "I don't know based on the documents" without calling the model
3. **Augment:** the retrieved chunks are added to the prompt as context
4. **Generate:** a local model (Ollama) answers using only that context

**Stack:** Python, FastAPI, ChromaDB, Ollama (qwen2.5:1.5b for answers, nomic-embed-text for embeddings)

**Knowledge base:** my NCAA athletic subsidy report, my patient no-show findings report, and a short profile, split into 22 chunks by section

## Results

I tested each change on the same 10 questions with known answers, plus 3 extra questions the documents don't cover.

| Round | Change | Correct | Partly | Wrong |
|---|---|---|---|---|
| 2 | Baseline (my documents, NextWork's prompt) | 3 | 2 | 5 |
| 3 | Tables rewritten as sentences | 3 | 2 | 5 |
| 3b | Plus temperature 0 | 4 | 0 | 6 |
| 4 | Plus strict prompt | 7 | 0 | 3 |
| 5 | Plus larger model (0.5b to 1.5b) | 8 | 1 | 1 |
| 6 | Plus relevance threshold | 9 | 1 | 0 |

Full question-by-question results are in `test_results.md`, and raw outputs for each round are in the `results_*.json` files.

## What I learned

**Retrieval was rarely the problem.** The right chunk was in the top 3 for every answerable question from the start. Most errors happened when the model read the context, not when it searched for it.

**The small model struggled with tables.** At baseline, every answer that required reading a table was wrong, and twice it took the value from the row next to the correct one. Converting table rows into sentences fixed some lookups but did not raise the overall score on its own.

**Randomness hid what was working.** With default settings, the same question could get a different answer each run, so a correct answer in one round turned wrong in the next. Setting temperature to 0 made results repeatable, which made fair comparisons possible.

**The strict prompt was the biggest single improvement.** Forcing one or two sentence answers, exact numbers, and no calculations took the score from 4 to 7. Every long answer in earlier rounds had invented math or details.

**A bigger model is not automatically more faithful.** The 1.5b model fixed two answers but replaced a neighbourhood name in my data ("Santos Dumont") with a real place it likely knew from training ("Santo Domingo"), while keeping the correct number.

**Prompt instructions alone did not stop made-up answers.** For questions outside my documents, the model invented answers in every round, including a fake enrollment number and "Paris" from its own knowledge. Measuring retrieval distances showed a clear gap: answerable questions scored 0.181 to 0.294, and out-of-scope questions scored 0.418 to 0.564. A cutoff of 0.35 in the code stopped every made-up answer.

## Limitations

- The 0.35 cutoff was chosen from 13 questions. A production system would tune it on a larger, more varied question set.
- Question 9 still returns the wrong neighbourhood name with the right rate.
- The test set is small, so these results show direction, not statistical certainty.

## Run it yourself

Requires Python 3.13 and [Ollama](https://ollama.com).

```
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python build_knowledge_base.py
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/docs` to ask questions, or run the test set in a second terminal:

```
python run_tests.py my_test_run
```

## Files

- `main.py`: the API, with the relevance threshold and strict prompt
- `build_knowledge_base.py`: splits documents into chunks, converts tables to sentences, and loads them into ChromaDB
- `run_tests.py`: asks all 13 test questions and saves the answers
- `test_results.md`: graded results and findings for every round
- `docs/`: the source documents