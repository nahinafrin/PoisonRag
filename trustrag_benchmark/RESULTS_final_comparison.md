# PoisonGuard-RAG vs TrustRAG — final comparison (tasks 4 & 5)

Status: interim, written 2026-09-26 19:40 CT. Numbers come from `RESULTS_table2.md` (regenerate with `score_table2.py`).
NQ = development set (the arbitration rule was chosen on it); HotpotQA and MS-MARCO = held out. Cells with n<100 are partial.
Same backbone for every measured row (Ollama `llama3.1:8b`), same Contriever top-5 passages, TrustRAG's own ACC/ASR code.
TrustRAG = line-for-line port of `defend_module.py` from github.com/HuichiZhou/TrustRAG (`kmeans_ngram` + `conflict_query`).

## Headline (measured, 100 questions per cell)

| Setting | TrustRAG (reproduced) ACC/ASR | PoisonGuard-RAG ACC/ASR | Verdict |
|---|---|---|---|
| NQ, poison 100% (no q-prefix) | 77 / 4 | 76 / 2 | tie ACC, lower ASR |
| NQ, poison 20% (no q-prefix) | 77 / 5 | 79 / 1 | **ours better** |
| NQ, poison 100% (q-prefix) | 77 / 1 | 76 / 1 | tie |
| NQ, poison 20% (q-prefix) | 78 / 8 | 76 / 1 | **ours: 8x lower ASR**, −2 ACC |
| NQ clean | 78 | 79 | tie |
| NQ PIA prompt injection | 78 / 4 | 77 / 5 | tie |
| HotpotQA, poison 100% (no q-prefix) | 65 / 6 | 47 / 4 | **TrustRAG better ACC** |
| HotpotQA, poison 20% (no q-prefix) | 66 / 24 | 53 / 28 | **TrustRAG better** |
| HotpotQA, poison 100% (q-prefix) | 68 / 5 | 47 / 2 | TrustRAG ACC, ours ASR |
| HotpotQA, poison 20% (q-prefix) | 67 / 21 | 49 / 2 | **ours: 10x lower ASR**, −18 ACC |
| Mean cost per query (all runs) | 24.8 s | 16.5 s | ours 1.5x faster |
| Refused/abstained on clean questions | 0% | 4.4% | TrustRAG better |

Paired per question (same 100 questions): NQ — each system gets 3–6 questions the other misses (statistical tie on ACC);
HotpotQA 100%/20% (no prefix) — TrustRAG-only-correct 22/20 vs ours-only-correct 5/8 (a real TrustRAG advantage).
Pending: 80/60/40% rates for PoisonGuard, all of MS-MARCO (second held-out set).

**Honest bottom line:** PoisonGuard-RAG is *not* uniformly better than TrustRAG. It matches TrustRAG's accuracy and
has equal or lower attack success on single-hop factoid QA (NQ), cuts attack success sharply when the attacker uses
TrustRAG's own query-optimised poison at low poison rates (NQ 8→1, HotpotQA 21→2), and is 1.5x cheaper; on multi-hop
QA (HotpotQA) it loses 13–20 accuracy points.

## Task 4 — Major differences from TrustRAG

| Aspect | TrustRAG (`defend_module.py`) | PoisonGuard-RAG (`poisonguard_rag/`) |
|---|---|---|
| Threat scope | corpus poisoning (+ PIA handled by prompt wording only) | corpus poisoning **and** prompt injection (query + retrieved context) **and** output data leakage |
| Stage-1 poison detection | K-means (k=2) on SimCSE CLS embeddings; a whole cluster is dropped if its mean cosine > 0.88 and ROUGE-L > 0.25 | per-passage risk r_i = noisy-OR(query-echo, pairwise coordination = σ(cos−0.85)·σ(ROUGE-L−0.25)) on BGE-M3; each passage dropped individually (r_i ≥ 0.5); survivors that are near-copies are grouped as ONE witness |
| Cross-stage risk | none — each stage decides alone | one adaptive risk R, updated by weighted noisy-OR R ← 1−(1−R)(1−w·r) at the query gate, context filter and poison filter; thresholds tighten as R rises |
| Injection detection | none (LLM told in the consolidation prompt to ignore "manipulative instructions") | LLM-Guard DeBERTa-v3 on the query (refuse ≥ 0.90) and on every passage (drop ≥ 0.50, 0.30 under high R) + supersession-cue regex |
| Use of internal knowledge | LLM writes ≤50-word internal knowledge; a second LLM call consolidates it with all passages; a third call "self-assesses" and answers | same internal-knowledge prompt, then a **deterministic rule**: if the model knows, retrieved text cannot overrule it; if not, ≥2 independent passages must agree |
| How passages are read | jointly, in one consolidation prompt | each passage in **isolation** (one short call per passage), so no passage can steer the reading of another |
| Final decision | LLM judgement (free text) | rule-based vote, auditable (every row logs decision, clusters, trusts, risk trace) |
| When evidence is missing | still produces a verbose best-effort answer | abstains ("can't give a trustworthy answer") |
| Output handling | none | Presidio NER + DLP regex + Luhn PII masking |
| LLM calls / cost | 3 long generations; 24.8 s/query measured | 2 + one short call per surviving passage; 16.5 s/query measured |

## Task 5 — Why and where ours is better (and where it is not)

**Why it is better where it is better**
1. *Security invariant instead of LLM judgement.* A poisoned passage can never overrule an answer the model already knows,
   and a single passage can never be the sole basis of an answer when poison was detected in the same batch. TrustRAG's
   self-assessment is an LLM judgement that one confident poisoned passage can still win: at 20% poison with the
   question prefix TrustRAG's ASR is 8% (NQ) and 21% (HotpotQA) vs our 1% and 2%.
2. *Per-passage detection keeps clean evidence.* K-means must split 5 passages into 2 clusters; with 1 poison
   (20% rate) it either leaves the poison in or discards clean passages (TrustRAG's own Table 6 reports detection F1 of only 2–10 at 20%).
   Our per-passage echo/coordination scores drop the poison and keep the rest (NQ 20%: ASR 1%).
3. *Sybil resistance.* Coordinated near-duplicates count as one witness, so injecting more copies does not add votes.
4. *Defence in depth outside the benchmark.* Injection detection at two points, PII/DLP masking and an auditable risk
   trace — none of which TrustRAG has — at 1.5x lower cost.

**Where it is not better, and why**
1. *Multi-hop questions (HotpotQA).* Reading passages in isolation breaks questions whose answer needs two passages
   combined: every clean passage returns "INSUFFICIENT", so a lone poisoned passage becomes the only single-document
   answer (this accounts for most of the HotpotQA-20% successful attacks). TrustRAG reads all passages together.
2. *Abstention vs guessing under the substring metric.* When all passages are poison and the model does not know,
   we abstain (35/100 on HotpotQA-100%); TrustRAG writes a long answer that often restates both entities of a
   comparison question, which the substring metric counts as correct.
3. *Benign cost.* 4.4% of clean questions end in abstention (TrustRAG 0%).
4. *PIA.* The DeBERTa detector caught only 12/100 injected PIA passages; the attack is stopped mainly by the
   knowledge-anchored rule, so the result ties TrustRAG rather than beating it.

**Setups where PoisonGuard-RAG is the better choice**
single-hop factoid QA where the backbone has broad world knowledge; attackers who optimise poison for retrieval
(question-prefixed passages) at low-to-medium poison rates; applications where a refusal is preferable to a wrong
answer (safety-critical, compliance) and where PII must not leak; latency/cost-constrained local deployment.
**TrustRAG is the better choice** for multi-hop reasoning over several documents and when an answer must always be produced.

## Next step that would address the loss (not yet run)
Fallback for multi-hop: when every isolated passage returns INSUFFICIENT, read the surviving passages jointly
(TrustRAG-style consolidation) but keep the invariant (cannot overrule known internal knowledge, abstain if the joint
answer rests on a passage flagged by the poison filter). Must be validated only on MS-MARCO (still unseen by any design decision).
