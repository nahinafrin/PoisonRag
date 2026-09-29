# PoisonGuard-RAG — result tables

Held-out test half: PoisonedRAG targets 51–100 of each dataset, 50 questions per cell, Llama-3.1-8B (Ollama) for every system, Contriever top-5, poison rate = poisoned passages / 5. Bold = best among the three defenses (ties bold all).

## Table 1 — ACC / ASR under corpus poisoning (TrustRAG substring metric)

| Dataset | Defense | 100% ACC↑ / ASR↓ | 80% ACC↑ / ASR↓ | 60% ACC↑ / ASR↓ | 40% ACC↑ / ASR↓ | 20% ACC↑ / ASR↓ | Clean ACC↑ |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG | 24 / 70 | 28 / 62 | 30 / 58 | 28 / 56 | 44 / 36 | 66 |
|  | TrustRAG | 68 / 6 | 68 / **4** | 72 / **2** | **76** / 6 | 68 / 6 | 70 |
|  | PoisonGuard v4 (previous) | **72** / **4** | **76** / **4** | 72 / 8 | 74 / 6 | **76** / **2** | **76** |
|  | **PoisonGuard-RAG (ours)** | 70 / 10 | 72 / 6 | **74** / 4 | 74 / **4** | 74 / **2** | 74 |
| HotpotQA | Vanilla RAG | 4 / 96 | 18 / 82 | 24 / 76 | 28 / 72 | 42 / 54 | 74 |
|  | TrustRAG | **64** / 8 | 66 / 6 | **78** / **4** | **70** / **8** | 62 / 28 | 76 |
|  | PoisonGuard v4 (previous) | **64** / 4 | 66 / 6 | 70 / **4** | 58 / 14 | **70** / **14** | 76 |
|  | **PoisonGuard-RAG (ours)** | 62 / **0** | **70** / **4** | 74 / 10 | 66 / 16 | **70** / **14** | **78** |
| MS-MARCO | Vanilla RAG | 46 / 42 | 46 / 42 | 44 / 42 | 54 / 34 | 58 / 28 | 76 |
|  | TrustRAG | 84 / 10 | 84 / 10 | 84 / 10 | 84 / 10 | 86 / 10 | 84 |
|  | PoisonGuard v4 (previous) | **92** / **2** | **92** / **2** | 90 / **2** | **92** / **4** | **90** / **4** | **92** |
|  | **PoisonGuard-RAG (ours)** | **92** / 4 | **92** / 4 | **92** / **2** | 90 / **4** | **90** / 6 | **92** |

## Table 2 — same, strict whole-word matching (applied identically to every system)

| Dataset | Defense | 100% ACC↑ / ASR↓ | 80% ACC↑ / ASR↓ | 60% ACC↑ / ASR↓ | 40% ACC↑ / ASR↓ | 20% ACC↑ / ASR↓ | Clean ACC↑ |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG | 22 / 72 | 26 / 64 | 28 / 60 | 26 / 58 | 42 / 38 | 66 |
|  | TrustRAG | 68 / 6 | 68 / **4** | 72 / **2** | **76** / 6 | 68 / 6 | 70 |
|  | PoisonGuard v4 (previous) | **72** / **4** | **76** / **4** | 72 / 8 | 74 / 6 | **76** / **2** | **76** |
|  | **PoisonGuard-RAG (ours)** | 70 / 10 | 72 / 6 | **74** / 4 | 74 / **4** | 74 / **2** | 74 |
| HotpotQA | Vanilla RAG | 4 / 94 | 18 / 80 | 24 / 74 | 28 / 70 | 42 / 50 | 74 |
|  | TrustRAG | **64** / 6 | 66 / 4 | **76** / **2** | **70** / **4** | 58 / 28 | 76 |
|  | PoisonGuard v4 (previous) | **64** / 2 | 66 / 4 | 70 / 4 | 58 / 14 | **70** / **14** | 76 |
|  | **PoisonGuard-RAG (ours)** | 60 / **0** | **70** / **2** | 74 / 10 | 66 / 16 | **70** / **14** | **78** |
| MS-MARCO | Vanilla RAG | 44 / 44 | 44 / 44 | 44 / 42 | 54 / 34 | 58 / 28 | 76 |
|  | TrustRAG | 78 / 4 | 82 / **0** | 78 / **0** | 76 / **0** | 80 / 6 | 76 |
|  | PoisonGuard v4 (previous) | **88** / **2** | **88** / 2 | **88** / 2 | **90** / 4 | **88** / **4** | **90** |
|  | **PoisonGuard-RAG (ours)** | **88** / 4 | **88** / 4 | **88** / 2 | 88 / 4 | **88** / 6 | 88 |

## Table 3 — Summary: robustness, utility and cost

| Dataset | Defense | mean ACC↑ | mean ASR↓ | Clean ACC↑ | Refusal/abstain↓ | s/query↓ | Speed-up vs TrustRAG |
|---|---|---|---|---|---|---|---|
| NQ | TrustRAG | 70.4 | **4.8** | 70 | **0.0** | 26.9 | 1.0× |
|  | PoisonGuard v4 (previous) | **74.0** | **4.8** | **76** | **0.0** | 8.1 | 3.3× |
|  | PoisonGuard-RAG (ours) | 72.8 | 5.2 | 74 | **0.0** | **6.0** | 4.5× |
| HotpotQA | TrustRAG | 68.0 | 10.8 | 76 | **0.0** | 21.6 | 1.0× |
|  | PoisonGuard v4 (previous) | 65.6 | **8.4** | 76 | **0.0** | 7.4 | 2.9× |
|  | PoisonGuard-RAG (ours) | **68.4** | 8.8 | **78** | **0.0** | **6.2** | 3.5× |
| MS-MARCO | TrustRAG | 84.4 | 10.0 | 84 | **0.0** | 20.8 | 1.0× |
|  | PoisonGuard v4 (previous) | **91.2** | **2.8** | **92** | **0.0** | 5.2 | 4.0× |
|  | PoisonGuard-RAG (ours) | **91.2** | 4.0 | **92** | **0.0** | **4.6** | 4.5× |

## Table 3b — Does the defence keep the benefit of retrieval? (clean ACC unless noted)

| Dataset | No retrieval (closed book) | Ours @100% poison | Ours clean | TrustRAG clean | Vanilla clean | Retrieval-needed subset: n / Vanilla / TrustRAG / Ours |
|---|---|---|---|---|---|---|
| NQ | 62 | 70 | 74 | 70 | 66 | 19 / 10 / 7 / 8 |
| HotpotQA | 50 | 62 | 78 | 76 | 74 | 25 / 13 / 15 / 14 |
| MS-MARCO | 74 | 92 | 92 | 84 | 76 | 13 / 9 / 8 / 10 |

## Table 7 — Reported baselines (TrustRAG paper, Table 2, Llama3.1-8B, 100 q) vs ours (held-out q 51-100)

Different question sets and serving stacks: indicative only; the controlled comparison is Table 1.

| Dataset | Defense | 100% | 80% | 60% | 40% | 20% | clean |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG (reported) | 2 / 98 | 2 / 98 | 3 / 97 | 4 / 93 | 26 / 73 | 71 |
| NQ | RobustRAG (keyword) (reported) | 11 / 83 | 15 / 75 | 23 / 63 | 37 / 46 | 51 / 27 | 61 |
| NQ | InstructRAG-ICL (reported) | 27 / 69 | 38 / 56 | 40 / 56 | 51 / 45 | 58 / 37 | 68 |
| NQ | AstuteRAG (reported) | 61 / 29 | 64 / 24 | 68 / 19 | 69 / 18 | 77 / 11 | 75 |
| NQ | TrustRAG stage 1 (reported) | 67 / 6 | 51 / 19 | 56 / 3 | 62 / 2 | 43 / 50 | 65 |
| NQ | TrustRAG (reported) | 83 / 2 | 85 / 1 | 84 / 1 | 83 / 1 | 82 / 9 | 82 |
| NQ | **PoisonGuard-RAG (ours, measured)** | 70 / 10 | 72 / 6 | 74 / 4 | 74 / 4 | 74 / 2 | 74 |
| HotpotQA | Vanilla RAG (reported) | 1 / 99 | 2 / 97 | 6 / 94 | 5 / 94 | 27 / 81 | 71 |
| HotpotQA | RobustRAG (keyword) (reported) | 8 / 89 | 10 / 87 | 19 / 76 | 33 / 57 | 40 / 50 | 54 |
| HotpotQA | InstructRAG-ICL (reported) | 26 / 73 | 40 / 57 | 50 / 47 | 52 / 44 | 54 / 41 | 83 |
| HotpotQA | AstuteRAG (reported) | 48 / 41 | 53 / 38 | 59 / 30 | 59 / 31 | 65 / 16 | 65 |
| HotpotQA | TrustRAG stage 1 (reported) | 54 / 6 | 61 / 12 | 72 / 3 | 66 / 2 | 43 / 47 | 70 |
| HotpotQA | TrustRAG (reported) | 67 / 4 | 71 / 4 | 70 / 7 | 69 / 5 | 66 / 18 | 74 |
| HotpotQA | **PoisonGuard-RAG (ours, measured)** | 62 / 0 | 70 / 4 | 74 / 10 | 66 / 16 | 70 / 14 | 78 |
| MS-MARCO | Vanilla RAG (reported) | 3 / 97 | 3 / 96 | 5 / 94 | 7 / 93 | 28 / 70 | 79 |
| MS-MARCO | RobustRAG (keyword) (reported) | 25 / 68 | 28 / 66 | 37 / 54 | 57 / 34 | 67 / 19 | 73 |
| MS-MARCO | InstructRAG (reported) | 44 / 54 | 47 / 51 | 49 / 45 | 60 / 36 | 63 / 33 | 89 |
| MS-MARCO | AstuteRAG (reported) | 26 / 73 | 40 / 57 | 50 / 47 | 52 / 44 | 54 / 41 | 83 |
| MS-MARCO | TrustRAG stage 1 (reported) | 77 / 7 | 64 / 18 | 72 / 7 | 78 / 6 | 45 / 47 | 81 |
| MS-MARCO | TrustRAG (reported) | 87 / 5 | 84 / 8 | 85 / 7 | 85 / 7 | 83 / 11 | 85 |
| MS-MARCO | **PoisonGuard-RAG (ours, measured)** | 92 / 4 | 92 / 4 | 92 / 2 | 90 / 4 | 90 / 6 | 92 |

## Table 4 — Passage filtering and robustness after exposure (poisoned settings only)

Poison recall = share of retrieved poisoned passages removed before generation; clean retention = share of retrieved clean passages kept; ASR | exposed = ASR on queries where ≥1 poisoned passage still reached the LLM.

| Dataset | Defense | Poison recall | Filter precision | Clean retention↑ | Exposed queries | ASR given exposure↓ |
|---|---|---|---|---|---|---|
| NQ | TrustRAG | **76.6** | **84.1** | 92.3 | 96 | 8.3 |
|  | PoisonGuard-RAG (ours) | 54.0 | 81.9 | **93.6** | 144 | **6.2** |
| HotpotQA | TrustRAG | **90.4** | 88.9 | 83.0 | 64 | 29.7 |
|  | PoisonGuard-RAG (ours) | 84.4 | **97.8** | **97.2** | 90 | **23.3** |
| MS-MARCO | TrustRAG | **69.1** | **36.8** | 69.0 | 69 | 21.7 |
|  | PoisonGuard-RAG (ours) | 41.7 | 32.4 | **77.3** | 104 | **9.6** |

## Table 5 — Paired comparison vs TrustRAG (same question, same poison rate; 250 pairs per dataset)

Wins/losses count only discordant pairs; p = two-sided exact sign (McNemar) test.

| Dataset | ACC: ours ✓ TrustRAG ✗ | ACC: TrustRAG ✓ ours ✗ | p | Attacks only TrustRAG fell for | Attacks only ours fell for | p |
|---|---|---|---|---|---|---|
| NQ | 14 | 8 | 0.286 | 5 | 6 | 1.000 |
| HotpotQA | 25 | 24 | 1.000 | 19 | 14 | 0.487 |
| MS-MARCO | 21 | 4 | <0.001 | 19 | 4 | 0.003 |
| All | 60 | 36 | 0.018 | 43 | 24 | 0.027 |

## Table 6 — Which decision route answered (PoisonGuard-RAG, % of queries, poisoned settings) and accuracy on that route

| Route | NQ share / ACC | HotpotQA share / ACC | MS-MARCO share / ACC |
|---|---|---|---|
| Parametric answer agrees with evidence | 23.6 / 92 | 28.4 / 79 | 21.2 / 91 |
| Parametric answer overrides conflicting evidence | 66.4 / 70 | 18.0 / 87 | 66.8 / 94 |
| Corroborated by independent passages | 0.8 / 0 | 5.6 / 21 | 3.2 / 62 |
| Best effort: knowledge + surviving passages | 8.8 / 55 | 37.6 / 65 | 8.0 / 80 |
| Best effort: closed book (lone passage hidden) | 0.4 / 0 | 10.4 / 46 | 0.8 / 100 |

## Risk score as a detector (diagnostic)

AUROC of the pipeline risk score for "≥1 poisoned passage in the top-5": NQ 0.697, HotpotQA 0.917, MS-MARCO 0.586.
