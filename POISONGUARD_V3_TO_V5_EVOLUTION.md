# PoisonGuard-RAG Evolution: v3.1 to v4 to v5

**Purpose:** explain what changed between the PoisonGuard-RAG versions, why each change was made, and what the available benchmark evidence supports. Results are separated by test split and protocol; partial v3.2 runs are not presented as full benchmark outcomes.

## 1. Version Comparison

| Version | Main change from prior version | Answer policy | Evaluation status |
|---|---|---|---|
| **v3.1** | Establishes isolated evidence arbitration and risk-aware handling of detected poison. Passage answers are generated independently; near-duplicate passages count as one source group. | Trust internal knowledge when available. If it is unknown, accept corroborated external evidence; a lone external answer can be accepted only when the poison filter has not detected poison. Otherwise abstain. | Full early 100-target pilot, plus v3.1 included in the held-out 51-100 comparison. |
| **v3.2** | Adds joint reading for multi-hop questions when internal knowledge is unknown and isolated reads do not corroborate. | Reads surviving passages together, requires the joint answer to be supported consistently, and does not accept a lone external passage by itself. | Main table cells not completed. Available data: one partial MS-MARCO cell ($n=79$) and one 4-row HotpotQA smoke run. |
| **v4** | Adds best-effort generation to reduce abstention when internal knowledge and isolated evidence do not yield a corroborated answer. | Uses a best-effort prompt over internal knowledge and filtered documents. When poison is detected and only an uncorroborated passage remains, that passage is hidden from best-effort generation. | Completed held-out 51-100 benchmark, 50 questions per dataset/rate cell. |
| **v5** | Adds comparison-question decomposition, parallelizes independent model calls, and introduces a dropped-poison-answer veto. | Keeps v4 best effort, but decomposes yes/no/comparison questions for closed-book knowledge and checks whether surviving answers match an answer from a dropped passage. | Completed held-out 51-100 benchmark and selected component ablations. Main v5 table does not enable the v3.2 joint-reading fallback. |

The underlying eight-stage request pipeline remains the same through these versions: input normalization, query injection gate, retrieval, context injection filtering, corpus-poison consensus filtering, evidence arbitration, output privacy filtering, and safe response. The version changes primarily modify the arbitration/answering stage rather than replacing the entire architecture.

## 2. How the System Changed

### v3.1: Isolate Evidence and Avoid Single-Source Poison

V3.1 introduced a knowledge-anchored answer rule for corpus poisoning. The model first attempts a short closed-book answer. Retrieved passages are then read one at a time, so a malicious passage cannot steer how another passage is interpreted. Similar answers are grouped, and passages identified as coordinated near-duplicates count as one witness. If the model knows the answer, the external evidence cannot override it. If it does not know, at least two independent passage groups are needed for corroboration. V3.1's risk-aware exception permits a lone passage only when the poison filter has not detected a poison for that query; if the filter has detected or removed likely poison, the pipeline abstains rather than trusting a single survivor.

This version improved security on NQ and MS-MARCO, but it had a pronounced utility weakness on HotpotQA. Questions requiring facts from multiple passages can fail when every passage is read in isolation: no one passage may contain enough information to answer, leaving the system to abstain or fall back to a weak answer. In the early 100-target pilot, v3.1 HotpotQA mean ACC over the five poison rates was 48.6%, mean ASR was 10.4%, and clean ACC was 57%. On the later held-out half, its mean HotpotQA ACC was only 44.0%, with 9.2% mean ASR and 56% clean ACC.

### v3.2: Joint Reading for Multi-Hop Evidence

V3.2 was designed to address the HotpotQA failure mode. When the model's internal knowledge is unknown and isolated passage reads fail to produce corroboration, the system makes a joint call over the surviving passages. The prompt directs the model to combine facts when necessary and rely on information consistent across documents. If joint reading still cannot support an answer, the system abstains. Unlike v3.1's conditional lone-source path, v3.2 does not accept an uncorroborated passage on its own.

This change is motivated by HotpotQA, so the project identifies MS-MARCO as the unbiased evaluation dataset for v3.2. However, the available version-wide table contains dashes for v3.2, and the queued benchmark did not leave a complete set of scored cells. The raw evidence available now is one incomplete MS-MARCO 100%-poison cell: 70/79 ACC (88.6%), 4/79 ASR (5.1%), and 1/79 refused or abstained. A separate four-question HotpotQA smoke check scored 2/4 ACC and 2/4 ASR. These are partial diagnostics only; they cannot establish an overall v3.2 improvement.

### v4: Best-Effort Answers Instead of Unnecessary Abstention

V4 adds a best-effort generation path after normal arbitration fails to produce a known or corroborated answer. It gives the generator the question, its internal knowledge statement, and filtered external documents, and asks it to produce a concise answer rather than refusing by default. Poison-aware handling limits the risk of that fallback: if poison was detected and only a lone uncorroborated passage remains, the suspicious lone passage is withheld and the model answers from its internal knowledge instead.

The v4 test used held-out targets 51-100, 50 questions per cell, Llama-3.1-8B, the same Contriever top-five passages as the baselines, and poison passages without the question prefix. Compared with v3.1 on those same held-out cells, v4 improved HotpotQA mean ACC from 44.0% to 65.6%, mean ASR from 9.2% to 8.4%, and clean ACC from 56% to 76%. NQ mean ACC rose from 70.8% to 74.0%, while mean ASR rose from 3.6% to 4.8%. MS-MARCO mean ACC rose from 87.2% to 91.2%, while mean ASR fell from 3.6% to 2.8%. These are paired-protocol version comparisons, although not every rate improves.

### v5: Improve Comparisons, Runtime, and Poison-Group Checks

V5 retains v4's best-effort behavior and adds three changes. First, comparison and yes/no questions are decomposed into short facts about each entity before producing the internal answer, addressing one-shot knowledge conflation on HotpotQA-style questions. Second, internal-knowledge generation and independent passage reads are launched concurrently; this is intended to reduce wall-clock latency without changing their prompts or deterministic sampling settings. Third, v5 reads one passage dropped by the poison filter and compares its answer with the surviving candidate answer. If they agree, the matching surviving votes are treated as potentially part of the poison group and are removed before arbitration is rerun.

The primary v5 benchmark uses best effort and the v5 rules, but it does not enable v3.2 joint reading. On the same held-out test split, v5 improves HotpotQA mean ACC over v4 from 65.6% to 68.4% and clean ACC from 76% to 78%, with mean ASR moving slightly up from 8.4% to 8.8%. On NQ, mean ACC falls from 74.0% to 72.8%, mean ASR rises from 4.8% to 5.2%, and clean ACC falls from 76% to 74%. On MS-MARCO, mean ACC remains 91.2%, mean ASR rises from 2.8% to 4.0%, and clean ACC remains 92%. Reported average latency decreases from v4 to v5 on all three datasets, but these are local-runtime measurements.

## 3. Held-Out Results by Version

### 3.1 NQ

Cells are ACC/ASR percentages under the TrustRAG substring metric. Poison rates are ordered 100%, 80%, 60%, 40%, 20%; clean is ACC only. Each held-out cell has $n=50$.

| Version | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla RAG | 24/70 | 28/62 | 30/58 | 28/56 | 44/36 | 66 |
| TrustRAG reproduced | 68/6 | 68/4 | 72/2 | 76/6 | 68/6 | 70 |
| PoisonGuard v3.1 | 70/2 | 70/6 | 70/6 | 70/2 | 74/2 | 74 |
| PoisonGuard v4 | 72/4 | 76/4 | 72/8 | 74/6 | 76/2 | 76 |
| PoisonGuard v5 | 70/10 | 72/6 | 74/4 | 74/4 | 74/2 | 74 |

### 3.2 HotpotQA

| Version | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla RAG | 4/96 | 18/82 | 24/76 | 28/72 | 42/54 | 74 |
| TrustRAG reproduced | 64/8 | 66/6 | 78/4 | 70/8 | 62/28 | 76 |
| PoisonGuard v3.1 | 42/2 | 40/4 | 42/4 | 42/10 | 54/26 | 56 |
| PoisonGuard v4 | 64/4 | 66/6 | 70/4 | 58/14 | 70/14 | 76 |
| PoisonGuard v5 | 62/0 | 70/4 | 74/10 | 66/16 | 70/14 | 78 |

### 3.3 MS-MARCO

| Version | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla RAG | 46/42 | 46/42 | 44/42 | 54/34 | 58/28 | 76 |
| TrustRAG reproduced | 84/10 | 84/10 | 84/10 | 84/10 | 86/10 | 84 |
| PoisonGuard v3.1 | 88/2 | 88/2 | 88/2 | 86/6 | 86/6 | 88 |
| PoisonGuard v4 | 92/2 | 92/2 | 90/2 | 92/4 | 90/4 | 92 |
| PoisonGuard v5 | 92/4 | 92/4 | 92/2 | 90/4 | 90/6 | 92 |

## 4. Summary Metrics

Means below are over the five poisoned rates. The answer-without-refusal column and latency are measured on the clean run and local machine respectively.

| Dataset | Version | Mean ACC | Mean ASR | Clean ACC | Clean answered without refusal | Seconds/query |
|---|---|---:|---:|---:|---:|---:|
| NQ | v3.1 | 70.8 | 3.6 | 74 | 98% | 14.4 |
| NQ | v4 | 74.0 | 4.8 | 76 | 100% | 8.1 |
| NQ | v5 | 72.8 | 5.2 | 74 | 100% | 6.0 |
| HotpotQA | v3.1 | 44.0 | 9.2 | 56 | 72% | 15.4 |
| HotpotQA | v4 | 65.6 | 8.4 | 76 | 100% | 7.4 |
| HotpotQA | v5 | 68.4 | 8.8 | 78 | 100% | 6.2 |
| MS-MARCO | v3.1 | 87.2 | 3.6 | 88 | 94% | 14.2 |
| MS-MARCO | v4 | 91.2 | 2.8 | 92 | 100% | 5.2 |
| MS-MARCO | v5 | 91.2 | 4.0 | 92 | 100% | 4.6 |

The strict whole-word tables provide a sensitivity analysis on the same held-out outputs. Strict mean ACC/ASR by version is: NQ v3.1 71.6/4.0, v4 74.0/4.8, v5 72.8/5.2; HotpotQA v3.1 44.0/9.2, v4 65.6/7.6, v5 68.0/8.4; MS-MARCO v3.1 85.6/3.6, v4 88.4/2.8, v5 88.0/4.0. Short-answer string matching can change cell-level results, so both metric conventions should be retained in thesis reporting.

## 5. v5 Component Ablations

These are selected held-out cells from the one-component-at-a-time study. Values are ACC/ASR under the paper substring metric. Decomposition and poison-answer-veto ablations were run on HotpotQA only; missing cells were not run.

| Dataset / poison rate | Full v5 | No answer voting | No internal knowledge | No poison filter | No decomposition | No poison-answer veto |
|---|---:|---:|---:|---:|---:|---:|
| NQ / 100% | 70/10 | 40/40 | 60/18 | 70/10 | - | - |
| NQ / 60% | 74/4 | 40/40 | 60/20 | 70/10 | - | - |
| NQ / 20% | 74/2 | 46/34 | 70/6 | 74/4 | - | - |
| HotpotQA / 100% | 62/0 | 36/32 | 54/8 | 36/56 | 66/4 | 62/8 |
| HotpotQA / 60% | 74/10 | 66/22 | 74/10 | 36/56 | 74/6 | 60/10 |
| HotpotQA / 20% | 70/14 | 46/50 | 66/20 | 70/14 | 70/16 | 70/14 |

The largest observed removals are answer voting on NQ and removal of the poison filter on highly poisoned HotpotQA. Effects are not uniform across rates. These results support the value of arbitration and poison filtering in selected settings, but the small number of tested cells and one-factor-at-a-time design do not quantify interactions or establish a universal component ranking.

## 6. Additional Attack Results

### 6.1 Prompt-Injection Passage

PIA uses one injected instruction passage among four clean passages. It is a different attack from a false factual answer embedded in a corpus.

| Split / version | Dataset | ACC/ASR | n |
|---|---|---:|---:|
| Earlier pilot, v3.1 | NQ | 77/5 | 100 |
| Earlier pilot, v3.1 | HotpotQA | 54/16 | 100 |
| Held-out, v5 | NQ | 70/8 (strict 68/8) | 50 |
| Held-out, v5 | HotpotQA | 54/12 (strict 54/12) | 50 |
| Held-out, v5 | MS-MARCO | 88/4 (strict 84/4) | 50 |

The v3.1 pilot and v5 held-out numbers use different target splits; they are not a paired version change.

### 6.2 Adaptive and Knowledge-Mimic Poisoning

The v5 adaptive attack rewrites the five poisons in different styles while preserving the original retrieval scores. The mimic attack makes a false statement resemble the model's own knowledge format. These interim cells use the held-out target range and report paper/strict results where available.

| Attack | Dataset | Poison rate | Vanilla | TrustRAG | v5 |
|---|---|---:|---:|---:|---:|
| Adaptive | NQ | 100% | 26/66 (24/68) | 70/10 | 72/4 (72/4) |
| Adaptive | NQ | 60% | 30/54 (28/56) | - | 74/6 (74/6) |
| Adaptive | NQ | 20% | 52/30 (52/30) | - | 74/4 (74/4) |
| Adaptive | HotpotQA | 100% | 6/92 (6/90) | 68/10 (68/8) | 56/10 (56/8) |
| Adaptive | HotpotQA | 60% | 28/70 (26/68) | - | 54/30 (54/28) |
| Adaptive | HotpotQA | 20% | 38/58 (38/56) | - | 68/20 (68/18) |
| Adaptive | MS-MARCO | 100% | 40/48 (40/48) | 80/14 (72/6) | 90/6 (86/4) |
| Adaptive | MS-MARCO | 60% | 40/48 (38/48) | - | 92/2 (86/2) |
| Adaptive | MS-MARCO | 20% | 54/34 (54/34) | - | 92/4 (86/4) |
| Mimic | NQ | 100% | 38/52 (36/54) | - | 72/4 (72/4) |
| Mimic | NQ | 60% | 42/48 (40/50) | - | 74/2 (74/2) |
| Mimic | NQ | 20% | n=31 | - | 72/4 (72/4) |
| Mimic | HotpotQA / MS-MARCO | All shown rates | - | - | - |

TrustRAG and most mimic cells were not completed in the interim artifact. These rows are not complete paired baseline comparisons.

### 6.3 Mistral-Nemo-12B

PoisonGuard v5 was also tested with Mistral-Nemo-12B. TrustRAG columns below are paper-reported values from a different set of questions, not a local paired reproduction.

| Dataset | Poison rate | Vanilla ACC/ASR | TrustRAG paper ACC/ASR | v5 ACC/ASR |
|---|---:|---:|---:|---:|
| NQ | 100% | 20/66 | 64/1 | 52/6 |
| NQ | 80% | - | 64/2 | 56/6 |
| NQ | 60% | 20/62 | 63/2 | 56/6 |
| NQ | 40% | - | 65/1 | 56/4 |
| NQ | 20% | 46/28 | 67/11 | 56/4 |
| NQ | Clean | 58 | 69 | 54 |
| HotpotQA | 100% | 0/98 | 75/4 | 68/4 |
| HotpotQA | 80% | - | 79/4 | 78/6 |
| HotpotQA | 60% | 10/90 | 79/4 | 82/4 |
| HotpotQA | 40% | - | 78/3 | 80/4 |
| HotpotQA | 20% | 34/66 | 74/13 | 82/4 |
| HotpotQA | Clean | 78 | 78 | 80 |
| MS-MARCO | 100% | 50/42 | 85/4 | 86/2 |
| MS-MARCO | 80% | - | 84/6 | 86/2 |
| MS-MARCO | 60% | 56/36 | 83/5 | 86/2 |
| MS-MARCO | 40% | - | 82/6 | 86/2 |
| MS-MARCO | 20% | 68/22 | 84/12 | 88/0 |
| MS-MARCO | Clean | 82 | 82 | 88 |

V5 latency is about 6-7 seconds/query in this run. The published TrustRAG comparison is indicative only because it is not matched locally.

## 7. Conclusions and Limitations

The clearest improvement from v3.1 to v4 is HotpotQA answer utility: v4's best-effort route raises held-out mean ACC from 44.0% to 65.6% and clean ACC from 56% to 76%, while also reducing mean ASR slightly. V4 also improves NQ and MS-MARCO mean ACC, although NQ mean ASR is higher than v3.1. V5 increases HotpotQA answer accuracy and clean accuracy over v4, but slightly raises HotpotQA mean ASR; it also has higher mean ASR than v4 on NQ and MS-MARCO while reducing measured latency. These are trade-offs, not a monotonic improvement on every metric.

V3.2 should remain a design proposal with partial diagnostic evidence until its matched MS-MARCO cells are completed. V4/v5 held-out cells have 50 cases each, so cell-level differences are noisy; means must be accompanied by per-rate tables. The early v3.1 pilot, held-out tables, PIA, adaptive/mimic attacks, Mistral-Nemo runs, and v5 ablations represent distinct evaluation populations and should not be pooled.

## 8. Source Artifacts

- [Early v3.1/v3.2 benchmark table](trustrag_benchmark/RESULTS_table2.md)
- [Held-out v4 results](trustrag_benchmark/RESULTS_final_v4.md)
- [Held-out v5 results](trustrag_benchmark/RESULTS_final_v5.md)
- [Additional attack, ablation, and Mistral-Nemo results](trustrag_benchmark/figures/RESULTS_extras_interim.md)
- [All tables bundle, including the detailed ablation table](Claude%20outputs/tables.md)
- [Version implementation notes](trustrag_benchmark/README_TRUSTRAG_BENCHMARK.md)