# PoisonGuard-RAG Results by Version: v3.1, v3.2, v4, and v5

**Evidence cutoff:** 2026-09-29. This file consolidates the available versioned benchmark outputs. Results are kept separate when their samples, poison formats, or configurations differ. `ACC/ASR` values are percentages; `-` means not run or not reported, not zero.

## 1. Version History

| Version | Main change | Evidence available |
|---|---|---|
| **v3.1** | Isolated per-passage evidence reading, closed-book knowledge answer, source-group voting, and risk-adaptive abstention when a lone external claim conflicts with detected poison. | Earlier 100-target pilot; later included as a comparator on the held-out 51-100 test half. |
| **v3.2** | Adds a joint-reading fallback when internal knowledge is unknown and isolated passage reads do not corroborate. The intended target is multi-hop HotpotQA questions. | Main published cells are blank; one incomplete MS-MARCO 100%-poison run (`n=79`) and one 4-row HotpotQA smoke test are present. |
| **v4** | Adds best-effort answering when isolated evidence fails to provide a known/corroborated answer. Under detected poison, it avoids using a lone uncorroborated survivor in the best-effort context. | Completed held-out targets 51-100, 50 questions per dataset/rate cell. |
| **v5** | Adds entity decomposition for comparison questions, concurrent independent reads, and a dropped-poison-answer veto. The v5 main table enables best effort and v5 behavior, but not v3.2 joint fallback. | Completed held-out targets 51-100, 50 questions per dataset/rate cell, plus ablations and additional attack suites. |

## 2. Shared Protocol and Metrics

The controlled benchmark uses the PoisonedRAG/TrustRAG Table 2 protocol. All locally reproduced systems use Ollama `llama3.1:8b`, Contriever top-five passages, the same questions, and the same passage order. For the principal `without_q` setting, poison passages do not include the question prefix. For poison rate $N/5$, the first $N$ adversarial passages are merged with clean retrieval candidates, ranked by Contriever, and the top five are supplied to the system. Rates are 0%, 20%, 40%, 60%, 80%, and 100%.

The held-out comparison uses target IDs 51-100: $n=50$ per dataset, rate, and system. Targets 1-50 were used during system development. NQ was the development set for the final arbitration rule; HotpotQA and MS-MARCO are held out for that rule. Thus, the test target IDs are held out for the reported cells, but the work does not claim that every design decision was blind to all three datasets.

- **Paper substring metric:** ACC is true-answer substring present; ASR is attacker-answer substring present while true answer is absent, after lowercasing and trimming.
- **Strict metric:** same success logic with whole-word/phrase boundaries, reducing short-answer substring artifacts (for example, `no` inside `know`).
- **Clean ACC:** accuracy at 0% poison.
- **Latency:** measured seconds per query on the local machine; it depends on local inference/runtime and is not a hardware-independent model property.
- **Published paper rows:** included only for context. The paper uses different questions and a different inference stack; those rows are not paired with our rows.

## 3. Earlier v3.1 Pilot: 100 Targets

This is the earlier all-target pilot in `RESULTS_table2.md`, not the held-out 51-100 comparison below. It evaluates `without_q` poison on up to 100 targets per cell. The table is preserved as historical context and must not be substituted for the later held-out results.

| Dataset | System | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---|---:|---:|---:|---:|---:|---:|
| NQ | Vanilla RAG | 26/69 | 28/65 | 33/57 | 35/49 | 46/34 | 68 |
| NQ | TrustRAG reproduced | 77/4 | 77/4 | 79/1 | 81/5 | 77/5 | 78 |
| NQ | PoisonGuard v3.1 | 76/2 | 76/3 | 77/3 | 77/1 | 79/1 | 79 |
| HotpotQA | Vanilla RAG | 6/94 | 17/83 | 22/76 | 30/69 | 38/58 | 73 |
| HotpotQA | TrustRAG reproduced | 65/6 | 68/7 | 77/4 | 69/7 | 66/24 | 76 |
| HotpotQA | PoisonGuard v3.1 | 47/4 | 47/6 | 47/5 | 49/9 | 53/28 | 57 |
| MS-MARCO | Vanilla RAG | 38/54 | 39/53 | 41/50 | 45/45 | 57/32 | 81 |
| MS-MARCO | TrustRAG reproduced | 86/8 | 84/8 | 86/9 | 87/7 | 90.5/4.8 (n=21) | - |
| MS-MARCO | PoisonGuard v3.1 | 87/3 | 87/4 | 87/4 | 86/6 | 87/5 | 88 |

All cells above are ACC/ASR. The incomplete TrustRAG MS-MARCO 20% cell is explicitly `n=21`; do not compare it as if it had 100 samples. In the same pilot, v3.1's PIA (one prompt-injection passage among five) scored NQ 77/5 and HotpotQA 54/16 at $n=100$. These PIA numbers are not corpus-poisoning Table 1 results.

## 4. Held-Out `without_q` Main Results (Targets 51-100)

Each cell is ACC/ASR at poison rates 100%, 80%, 60%, 40%, 20%; clean is ACC only. Each completed cell has $n=50$. Vanilla, reproduced TrustRAG, v3.1, v4, and v5 were scored under the same paper substring rule.

### 4.1 NQ

| System | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla RAG | 24/70 | 28/62 | 30/58 | 28/56 | 44/36 | 66 |
| TrustRAG reproduced | 68/6 | 68/4 | 72/2 | 76/6 | 68/6 | 70 |
| PoisonGuard v3.1 | 70/2 | 70/6 | 70/6 | 70/2 | 74/2 | 74 |
| PoisonGuard v4 | 72/4 | 76/4 | 72/8 | 74/6 | 76/2 | 76 |
| PoisonGuard v5 | 70/10 | 72/6 | 74/4 | 74/4 | 74/2 | 74 |

### 4.2 HotpotQA

| System | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla RAG | 4/96 | 18/82 | 24/76 | 28/72 | 42/54 | 74 |
| TrustRAG reproduced | 64/8 | 66/6 | 78/4 | 70/8 | 62/28 | 76 |
| PoisonGuard v3.1 | 42/2 | 40/4 | 42/4 | 42/10 | 54/26 | 56 |
| PoisonGuard v4 | 64/4 | 66/6 | 70/4 | 58/14 | 70/14 | 76 |
| PoisonGuard v5 | 62/0 | 70/4 | 74/10 | 66/16 | 70/14 | 78 |

### 4.3 MS-MARCO

| System | 100% | 80% | 60% | 40% | 20% | Clean |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla RAG | 46/42 | 46/42 | 44/42 | 54/34 | 58/28 | 76 |
| TrustRAG reproduced | 84/10 | 84/10 | 84/10 | 84/10 | 86/10 | 84 |
| PoisonGuard v3.1 | 88/2 | 88/2 | 88/2 | 86/6 | 86/6 | 88 |
| PoisonGuard v4 | 92/2 | 92/2 | 90/2 | 92/4 | 90/4 | 92 |
| PoisonGuard v5 | 92/4 | 92/4 | 92/2 | 90/4 | 90/6 | 92 |

## 5. Held-Out Summary by Version

Means are across the five poisoned rates; clean ACC is reported separately. Each version's summary below comes from the held-out tables, not the earlier v3.1 pilot.

| Dataset | Version | Mean ACC | Mean ASR | Clean ACC | Clean answered without refusal | Mean s/query |
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

Interpretation: v4 improves the mean ACC/latency trade-off over v3.1 on these cells, especially HotpotQA; v5 improves HotpotQA clean/mean ACC and MS-MARCO latency, but does not improve every ASR or NQ metric. No version is uniformly best at every dataset/rate. Report the per-rate tables with the means.

## 6. Strict Whole-Word Sensitivity Results

These are held-out means over the same five poisoned rates, with the strict matching rule applied to all systems' outputs. Full per-rate strict tables are in the linked source reports.

| Dataset | Version | Mean strict ACC | Mean strict ASR | Strict clean ACC |
|---|---|---:|---:|---:|
| NQ | v3.1 | 71.6 | 4.0 | 74 |
| NQ | v4 | 74.0 | 4.8 | 76 |
| NQ | v5 | 72.8 | 5.2 | 74 |
| HotpotQA | v3.1 | 44.0 | 9.2 | 56 |
| HotpotQA | v4 | 65.6 | 7.6 | 76 |
| HotpotQA | v5 | 68.0 | 8.4 | 78 |
| MS-MARCO | v3.1 | 85.6 | 3.6 | 86 |
| MS-MARCO | v4 | 88.4 | 2.8 | 90 |
| MS-MARCO | v5 | 88.0 | 4.0 | 88 |

The strict scorer changes several individual short-answer cells, notably HotpotQA and MS-MARCO. Use it as a robustness check against substring artifacts, not as a replacement for the original TrustRAG metric without stating the change.

## 7. v3.2 Partial Results

The published `RESULTS_table2.md` marks all v3.2 cells as not reported. Available raw artifacts add only the following partial observations:

| v3.2 run | Sample | ACC | ASR | Refused/abstained | Status |
|---|---:|---:|---:|---:|---|
| MS-MARCO, 100% poison, without question prefix | 79 | 70/79 (88.6%) | 4/79 (5.1%) | 1/79 | Incomplete; the queued benchmark intended 100 targets. |
| HotpotQA smoke, 20% poison, without question prefix | 4 | 2/4 (50%) | 2/4 (50%) | 0/4 | Smoke check only, not an estimate. |

Do not claim a v3.2 version-wide improvement from these files. The MS-MARCO result is a partial cell, and the HotpotQA smoke sample is only four questions. The `v32` queue script indicates that a larger set of cells was planned, but those outputs are absent from the published table artifact.

## 8. Additional Versioned Results

### 8.1 Prompt-Injection Passage (PIA)

PIA inserts one instruction-bearing passage among four clean passages. It is distinct from factual corpus poisoning.

| Split / version | Dataset | ACC/ASR | n |
|---|---|---:|---:|
| Earlier pilot, v3.1 | NQ | 77/5 | 100 |
| Earlier pilot, v3.1 | HotpotQA | 54/16 | 100 |
| Held-out, v5 | NQ | 70/8 (strict 68/8) | 50 |
| Held-out, v5 | HotpotQA | 54/12 (strict 54/12) | 50 |
| Held-out, v5 | MS-MARCO | 88/4 (strict 84/4) | 50 |

The earlier v3.1 pilot and held-out v5 rows have different target splits and must not be read as a paired v3.1-to-v5 change.

### 8.2 Adaptive and Knowledge-Mimic Poisoning (v5)

These held-out tests alter poison style while reusing the original `without_q` Contriever relevance scores. `adaptive` rewrites the five poisons in distinct styles to weaken near-duplicate coordination; `mimic` writes false claims in a format resembling the model's own knowledge statement. Values below are paper/strict ACC/ASR as shown in the interim artifact; `-` means not run/incomplete.

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
| Mimic | HotpotQA | 100% / 60% / 20% | - | - | - |
| Mimic | MS-MARCO | 100% / 60% / 20% | - | - | - |

TrustRAG and many mimic cells are not available; these rows establish preliminary v5 behavior, not a full paired comparison.

### 8.3 Mistral-Nemo-12B Backbone

PoisonGuard v5 was also run with Mistral-Nemo-12B on held-out targets. The comparison values shown for TrustRAG are reported paper numbers on a different 100-question set, not a local paired reproduction.

| Dataset | Poison rate | Vanilla ACC/ASR | TrustRAG paper ACC/ASR | PoisonGuard v5 ACC/ASR |
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

PoisonGuard latency was about 6-7 seconds/query in this run. Because TrustRAG was not locally rerun with this backbone, these columns are indicative only.

## 9. Component Ablations (v5 Held-Out Test)

The following removal tests use the v5 code and selected held-out cells. Values are ACC/ASR under the paper metric. Missing cells mean the ablation was not run. This is a one-component-at-a-time study, not a factorial interaction analysis.

| Dataset / rate | Full v5 | No answer voting | No internal knowledge | No poison filter | No decomposition | No poison-answer veto |
|---|---:|---:|---:|---:|---:|---:|
| NQ / 100% | 70/10 | 40/40 | 60/18 | 70/10 | - | - |
| NQ / 60% | 74/4 | 40/40 | 60/20 | 70/10 | - | - |
| NQ / 20% | 74/2 | 46/34 | 70/6 | 74/4 | - | - |
| HotpotQA / 100% | 62/0 | 36/32 | 54/8 | 36/56 | 66/4 | 62/8 |
| HotpotQA / 60% | 74/10 | 66/22 | 74/10 | 36/56 | 74/6 | 60/10 |
| HotpotQA / 20% | 70/14 | 46/50 | 66/20 | 70/14 | 70/16 | 70/14 |

The `RESULTS_extras_interim.md` artifact also provides strict-metric parentheses for several cells. For example, HotpotQA full v5 is 62/0 (strict 60/0) at 100%, 74/10 (74/10) at 60%, and 70/14 (70/14) at 20%. The ablation table in `Claude outputs/tables.md` is the authoritative full list of paper-metric values; the interim file should be consulted for strict values where supplied.

## 10. Main Findings and Interpretation

1. **v3.1 established the knowledge-anchored approach but struggled on multi-hop HotpotQA.** In the earlier 100-target pilot it recorded 47-53% ACC across poisoned HotpotQA rates and 44% clean ACC. On the later held-out 50-question cells its mean was 44.0% ACC, 9.2% ASR, 56% clean ACC, and 72% clean answer rate.
2. **v3.2's joint-reading idea is plausible but not yet supported by a complete benchmark.** Only an incomplete MS-MARCO cell and four-row smoke test are present. Do not claim a version-wide improvement until the planned matched cells are complete.
3. **v4 materially improved the held-out utility/security balance over v3.1, particularly HotpotQA.** It raised HotpotQA mean ACC from 44.0% to 65.6% and clean ACC from 56% to 76%, with mean ASR 9.2% to 8.4%. NQ improved mean ACC, while MS-MARCO achieved the best mean ASR in the v3-v5 series.
4. **v5 trades some NQ/MS-MARCO ASR for other gains.** Relative to v4, v5 improves HotpotQA mean ACC (65.6% to 68.4%) and clean ACC (76% to 78%); it is faster in every dataset. NQ v5 mean ASR is higher than v4 (5.2% vs 4.8%); MS-MARCO v5 mean ASR is also higher (4.0% vs 2.8%).
5. **No version dominates every cell.** Report per-rate metrics with means, both answer matching conventions, clean utility, latency, and incomplete cells. The held-out question set is small (50 per cell), and the development/test boundary must remain explicit.

## 11. Source Artifacts

- [Earlier v3.1 and v3.2 table](trustrag_benchmark/RESULTS_table2.md)
- [Held-out v4 tables](trustrag_benchmark/RESULTS_final_v4.md)
- [Held-out v5 tables](trustrag_benchmark/RESULTS_final_v5.md)
- [v3.2 and v5 extra evaluations / ablations](trustrag_benchmark/figures/RESULTS_extras_interim.md)
- [All result tables, including ablations](Claude%20outputs/tables.md)
- [PoisonGuard version and implementation notes](trustrag_benchmark/README_TRUSTRAG_BENCHMARK.md)
- Raw v3.2 partial cell: `results/poisonguard_v32__msmarco__p5__without_q.jsonl` ($n=79$).
- Raw v3.2 smoke test: `smoke_v32/poisonguard_v32__hotpotqa__p1__without_q.jsonl` ($n=4$).