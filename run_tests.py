import json
import sys
import requests

ROUND_NAME = sys.argv[1] if len(sys.argv) > 1 else "test_run"

QUESTIONS = [
    ("What was the median subsidy dependence?", "63.8%"),
    ("How many schools rely on subsidies for more than half their athletic money?", "151 of 236"),
    ("Which conference has the lowest average subsidy dependence?", "SEC, about 4%"),
    ("What is the average subsidy dependence for Mid-American conference schools?", "About 66%"),
    ("Where does the NCAA data come from?", "Knight-Newhouse College Athletics Database, FY2024"),
    ("What is the overall no-show rate?", "20.19%"),
    ("What is the no-show rate for same-day appointments?", "4.65%"),
    ("Which age group has the highest no-show rate?", "18-34, at 23.98%"),
    ("Which neighbourhood has the highest no-show rate?", "Santos Dumont, at 28.92%"),
    ("How many students attend the University of Mary Washington?", "The context does not say"),
]

results = []
for i, (question, expected) in enumerate(QUESTIONS, start=1):
    print(f"Asking question {i} of {len(QUESTIONS)}...")
    response = requests.get("http://127.0.0.1:8000/ask", params={"question": question})
    data = response.json()
    results.append({
        "number": i,
        "question": question,
        "expected": expected,
        "answer": data["answer"],
        "sources": data["sources"],
    })

filename = f"results_{ROUND_NAME}.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

for r in results:
    print(f"\n{r['number']}. {r['question']}")
    print(f"   Expected: {r['expected']}")
    print(f"   Answer:   {r['answer']}")

print(f"\nSaved to {filename}")