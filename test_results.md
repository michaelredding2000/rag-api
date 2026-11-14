\# RAG API Test Results



\## Round 1: Profile only (NextWork tutorial)



Model: qwen2.5:0.5b | Embeddings: nomic-embed-text | Chunks retrieved per question: 2



\### Test 1

Question: What is my career goal?

Expected: Junior AI engineer or prompt engineer at a federal contractor in the DC area

Right chunk retrieved: Yes (career goal paragraph was the top match)

Answer correct: Mostly

Made-up details: Said a federal contractor is "likely a government agency" (wrong, contractors are private companies). Added a goal of moving to a senior position, which is not in the profile.

Notes: Second retrieved chunk (citizenship) was not relevant. The search always returns 2 chunks, so it grabs the next closest one.



\### Test 2

Question: What tools and languages do I know?

Expected: Python, SQL, Power BI, Tableau, Excel

Right chunk retrieved: Yes, but ranked second. The career goal paragraph ranked first even though it does not answer the question.

Answer correct: Mostly. All five tools listed correctly.

Made-up details: Listed NextWork as a tool, and called it "a powerful project management and collaboration tool" (wrong, it is a learning platform). Ended with an unrelated sentence: "You are an AI assistant that helps you know more and find answers to your queries."

Notes: The model added information beyond the context both times so far. Pattern: grounds the core fact, then pads.



\### Test 3

Question: What is my favorite food?

Expected: The context does not say

Right chunk retrieved: N/A. Nothing in the profile covers this, but ChromaDB still returned 2 chunks (citizenship and name) because it always returns its closest matches.

Answer correct: Yes. It said the context has no information about my favorite food.

Made-up details: None

Notes: The prompt instruction "If the context doesn't contain relevant information, say so" kept the model from inventing an answer.



\### Round 1 summary

3 tests: 1 fully correct (correctly refused), 2 mostly correct with made-up details added.

Pattern: retrieval finds the right chunk, the model grounds the core fact, then adds details that aren't in the context.



\## Round 2: Portfolio documents (baseline)



Documents: profile.txt, ncaa\_subsidy\_report.md, noshow\_findings\_report.md (22 chunks, split by section)

Model: qwen2.5:0.5b | Chunks retrieved: 3 | Prompt: original NextWork prompt



| # | Question | Expected | Answer given | Right chunk retrieved | Correct |

|---|---|---|---|---|---|

| 1 | What was the median subsidy dependence? | 63.8% | 34% (took the FBS average from the table) | Yes, top chunk | No |

| 2 | How many schools rely on subsidies for more than half their athletic money? | 151 of 236 | 151 of 236, but long-winded and added unrelated subdivision averages | Yes, top chunk | Yes |

| 3 | Which conference has the lowest average subsidy dependence? | SEC, about 4% | Said the context did not have the answer, and wrongly claimed the Big Ten and ACC are No Football schools | Yes, top chunk (conference table) | No |

| 4 | What is the average subsidy dependence for Mid-American conference schools? | About 66% | About 63% (took the Conference USA row above it), after quoting the 66% figure in its own answer | Yes, top chunk (conference table) | No |

| 5 | Where does the NCAA data come from? | Knight-Newhouse College Athletics Database, FY2024 | Knight-Newhouse College Athletics Database, FY2024, 240 schools, inflation-adjusted | Yes, but ranked third | Yes |

| 6 | What is the overall no-show rate? | 20.19% | 20.19%, but presented a reworded line as a direct quote | Yes, top chunk | Yes |

| 7 | What is the no-show rate for same-day appointments? | 4.65% | 23.08% (Saturday's no-show rate from Finding 1) | Yes, but the table ranked second behind the day-of-week bullets | No |

| 8 | Which age group has the highest no-show rate? | 18-34, at 23.98% | 18-34 (correct), but invented a false stat combining two table cells, and never gave the 23.98% rate | Yes, top chunk | Partly |

| 9 | Which neighbourhood has the highest no-show rate? | Santos Dumont, at 28.92% | Santa Cecilia, 27.46% (the row 2 entry) | Yes, top chunk | No |

| 10 | How many students attend the University of Mary Washington? | The context does not say | Did not give a number, but said UMW is "based in McLean, Virginia" (that is my location, not UMW's) and that it is a public university (true, but not in the documents) | N/A, not in any document | Partly |



\### Round 2 summary

Score: 3 correct, 2 partly correct, 5 wrong out of 10.



Retrieval worked well. The chunk with the answer was in the top 3 for all 9 answerable questions, and ranked first for 7 of them.



Generation was the problem. The main finding is that the model struggles to read markdown tables:

\- Answers stated in sentences or bullets were correct (questions 2, 5, 6). On question 8, the correct age group came from a summary sentence under the table.

\- Every answer that required reading a table was wrong (questions 3, 4, 7, 9). Question 1 was also wrong: the answer was in a sentence, but a table in the same chunk pulled the model toward the wrong number.

\- Two answers took the row next to the correct one (questions 4 and 9).

\- The model also invented details: a quote that is not in the report (question 4), a reworded line presented as a quote (question 6), a false stat built from two table cells (question 8), and a wrong location (question 10).



Next experiments, one at a time, rerunning the same 10 questions each time:

1\. Rewrite tables as sentences before they go into the knowledge base

2\. A stricter prompt: answer only from the context, quote the exact number, keep it short

3\. A larger model: qwen2.5:1.5b



\## Round 3: Tables rewritten as sentences



Change: the build script converts every markdown table row into a sentence, like "Row: Rank is 1, Neighbourhood is SANTOS DUMONT, Total is 1,276, No-Show Rate is 28.92%."

Model: qwen2.5:0.5b | Chunks retrieved: 3 | Prompt: original NextWork prompt | Temperature: default



Score: 3 correct, 2 partly correct, 5 wrong (same total as baseline, different questions).

Fixed: questions 3 and 9 (finding the top row of a table).

Got worse: question 6 was correct at baseline, but this time the model did unrequested math and answered 4.53%.

Finding: the default settings add randomness, so the same question can get a different answer each run. That makes it impossible to tell whether a change helped.



\## Round 3b: Temperature set to 0



Change: added temperature 0 so the model gives the same answer every run.

Score: 4 correct, 0 partly correct, 6 wrong.

Finding: every correct answer was one or two sentences, and every long answer was wrong. When the model started "analyzing," it invented structure, math, and facts. Question 10 claimed 2,023 students, taken from "2023 Computer Science graduate."



\## Round 4: Strict prompt



Change: rules moved into a system message. Answer in one or two sentences, copy numbers exactly, do not calculate, do not explain reasoning, add nothing that is not in the context, and reply "I don't know based on the documents" when the answer is missing.

Model: qwen2.5:0.5b | Temperature: 0 | Chunks retrieved: 3



| # | Expected | Answer given | Correct |

|---|---|---|---|

| 1 | 63.8% | \~34% | No |

| 2 | 151 of 236 | 151 schools | Yes |

| 3 | SEC, about 4% | Southeastern (SEC) | Yes |

| 4 | About 66% | \~66% | Yes |

| 5 | Knight-Newhouse College Athletics Database | Knight-Newhouse College Athletics Database | Yes |

| 6 | 20.19% | 20.19% | Yes |

| 7 | 4.65% | 4.65% | Yes |

| 8 | 18-34, at 23.98% | Gave the 0-17 row (21.90%) | No |

| 9 | Santos Dumont, at 28.92% | Santos Dumont | Yes |

| 10 | The context does not say | 100 | No |



Score: 7 correct, 0 partly correct, 3 wrong.



\## Results so far



| Round | Change | Correct | Partly | Wrong |

|---|---|---|---|---|

| 2 | Baseline | 3 | 2 | 5 |

| 3 | Tables as sentences | 3 | 2 | 5 |

| 3b | Plus temperature 0 | 4 | 0 | 6 |

| 4 | Plus strict prompt | 7 | 0 | 3 |



Biggest single improvement: the strict prompt. Forcing short answers stopped the model from inventing math and details.

Still failing: question 1 (picks the FBS row over the median sentence in the same chunk every time), question 8 (picked the first row instead of the highest), question 10 (ignored the "I don't know" rule and made up a number).

Next: test a larger model (qwen2.5:1.5b) with the same setup.

