# PoisonGuard-RAG — final thesis pipeline

Secure RAG against **prompt injection** (direct and indirect) and **corpus poisoning / knowledge
corruption** (PoisonedRAG), with output data-loss prevention. Fully local: Ollama `llama3.1:8b`,
LLM-Guard DeBERTa-v3, BGE-M3 + FAISS, Presidio.

```
python -m poisonguard_rag.pipeline --question "who wrote the hobbit" --docs my_passages.txt
```

## Stages (file = job)

| # | File | Job | Blocks? |
|---|---|---|---|
| 1 | `input_normalization.py` (+ `text_normalizer.py`) | ftfy/mojibake repair, hidden chars, de-obfuscation, contractions | never |
| 2 | `query_injection_gate.py` | DeBERTa-v3 injection risk r_q → adaptive risk R; refuse if r_q ≥ 0.90 | only real injections |
| 3 | `retriever.py` | BGE-M3 + FAISS top-k (any retriever can be plugged in) | – |
| 4 | `context_injection_filter.py` (+ `supersession_cue.py`) | drop instruction-bearing / "correction"-framed passages; threshold 0.50 → 0.30 when R > 0.45 | drops passages |
| 5 | `poison_consensus_filter.py` | query-echo + coordination (cosine × ROUGE-L) poison risk; drop r_i ≥ 0.5; sybil groups; → R | drops passages |
| 6 | `evidence_arbitration.py` | knowledge-anchored, isolated, sybil-resistant answer (see below) | abstains if no evidence |
| 7 | `output_privacy_filter.py` | Presidio PII + DLP regex + Luhn masking | never (masks) |
| 8 | `safe_response.py` | answer / abstention / refusal | – |
| – | `state.py` | per-query state + noisy-OR risk R ← 1 − (1 − R)(1 − w·r) | – |
| – | `pipeline.py` | orchestrator + CLI | – |

**Evidence arbitration (stage 6) — the security invariant.** Retrieved text may *add* knowledge the
model lacks but can never *overrule* knowledge the model states it has. If the backbone knows the answer
(it writes a ≤50-word statement, not "I don't know"), that answer is returned with the statement as
justification. Only when it does not know are the passages used, each read in isolation, and an answer
counts as corroborated only with ≥ 2 independent (non-coordinated) passages. A single uncorroborated passage is
accepted only if the poison stage saw no poison for this query (no drop and R < 0.5); otherwise the system abstains
(risk-adaptive abstention, v3.1 — added after inspecting the first 13 HotpotQA rows; MS-MARCO is fully held out).

## Mapping from the earlier 13-step pipeline (`..\step4 dataset\`, `..\dataset\`)

| Earlier step | Now |
|---|---|
| 1 user input, 2 normalization | `input_normalization.py` (length check no longer refuses) |
| 3c C3RF fusion gate (DeBERTa + Llama-Guard-1B) | `query_injection_gate.py` (DeBERTa only) |
| 4 embedding, 5 vector search | `retriever.py` |
| 6 context sanitization | `context_injection_filter.py` |
| 6b poison consensus (added for TrustRAG comparison) | `poison_consensus_filter.py` |
| 9d evidence arbitration (added) | `evidence_arbitration.py` (knowledge-anchored rule) |
| 11 output sanitization (Presidio part), 12 DLP | `output_privacy_filter.py` |
| 13 safe response | `safe_response.py` |

## Removed, with the evidence (TrustRAG benchmark logs, 1000 NQ runs of the earlier pipeline)

| Removed | Why |
|---|---|
| Llama-Guard-1B in the input gate (part of 3c) | refused 20/1000 benign questions ("who wrote the song *What Child Is This*" → S4), caught 0 attacks |
| Llama-Guard-1B output verdict (part of 11) | refused 10/1000 benign answers, caught 0 attacks |
| Step 10 grounding judge + closed-loop risk controller | 8/1000 benign refusals, 304 extra re-verifications, 0 attacks caught: a poisoned answer *is* grounded in the poisoned passage, so grounding cannot detect it |
| Step 9 three-model fused ensemble | all three models read the same poisoned context, so they agree on the poisoned answer (agreement is not independence); 3 models × cost; replaced by stage 6 |
| Step 9a isolate-aggregate, 9b knowledge-conflict probe, 9c routed generator | superseded by stage 6 (which contains isolation + internal knowledge) |
| Step 7 cross-encoder rerank floor | no security effect on these attacks (poison is written to be relevant); all top-k passages are kept, as in TrustRAG, so stage 6 has every available witness |
| Step 8 prompt template | stage 6 has its own prompts |
| Step 3d semantic-intent gate, multi-vector detector, calibration | experimental, off by default, no effect on these attacks |

The earlier code is **kept unchanged** in `..\step4 dataset\` and `..\dataset\` because the locked thesis
results and the "Ours v1 / v2" benchmark rows are produced by it.

## v3.2 — multi-hop joint-reading fallback (added 2026-09-26 22:45 CT)
HotpotQA showed that reading passages only in isolation fails on questions that need two passages combined.
v3.2: when the model does not know the answer AND isolated reading gives no corroborated answer, the surviving
passages are read **jointly** (one call, told that some documents may be planted and to use only facts consistent
across documents). If the joint reading also gives no answer the pipeline abstains; a lone uncorroborated passage
is never accepted on its own any more. The knowledge-anchored invariant is unchanged.
Evaluation discipline: this change was motivated by HotpotQA, so **MS-MARCO is the only unbiased test of v3.2**
(`poisonguard_v32__msmarco__*` vs `trustrag__msmarco__*`). `pipeline.run(..., joint_fallback=True)` is the default;
the benchmark row "poisonguard" is v3.1 (joint_fallback=False) for the before/after comparison.
