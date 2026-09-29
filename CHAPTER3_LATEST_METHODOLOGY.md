# Chapter 3: System Design and Methodology

## 3.1 Methodology

### 3.1.1 Research Design and Scope

This study implements and evaluates PoisonGuard-RAG, a local security pipeline for retrieval-augmented generation. The design addresses two related but distinct threats: instruction-based attacks, which attempt to override model or application instructions, and corpus-poisoning attacks, which place plausible but incorrect factual claims in retrieved documents. It also applies output privacy controls to reduce the exposure of personal and credential-like data.

The system is evaluated as a pipeline around a fixed open-weight generator rather than as a newly trained language model. No supervised fine-tuning is performed for the reported PoisonGuard v5 tables. The main corpus-poisoning mechanism is a combination of passage-level risk scoring and evidence arbitration: suspicious passages can be filtered, coordinated sources count as one witness, and an uncorroborated external claim should not displace an answer the model already knows.

The threat model assumes that an attacker can influence one or more passages retrieved for a target question and can select an incorrect answer to promote. The benchmark includes query-prefixed and query-free poison formats, direct prompt-injection passages, style-diverse poisons, and poisons written to resemble the model's own knowledge. These attack settings are measured separately because they exercise different signals. The work does not claim complete protection against semantic misinformation, all adaptive attacks, or all RAG deployments.

### 3.1.2 Research and Evaluation Workflow

The research workflow follows four stages, consistent with the earlier project report:

1. **Threat modeling:** define direct query injection, indirect instruction injection, factual corpus poisoning, privacy leakage, and benign utility as separate evaluation concerns.
2. **Dataset preparation:** prepare target questions, correct and attacker-selected incorrect answers, clean retrieval passages, and adversarial passages. Split target IDs so development questions are not reported as the main test cells.
3. **Framework implementation:** compose normalization, injection screening, context filtering, poison-consensus scoring, evidence arbitration, and output privacy protection into one local pipeline.
4. **Testing and review:** compare against vanilla RAG and a reproduced TrustRAG baseline on fixed contexts; report attack success, answer accuracy, refusal/abstention, latency, paired results, component ablations, and limitations.

The methodology separates detector behavior from answer-level outcomes. A passage-filter decision is not itself an end-to-end success: final claims are scored by whether the generated answer contains the attacker's target answer without the correct answer. Clean question performance and latency are reported alongside security metrics.

### 3.1.3 Dataset and Benchmark Construction

The controlled corpus-poisoning benchmark uses target questions from Natural Questions (NQ), HotpotQA, and MS-MARCO. Each target record has a question, a correct answer, an attacker-selected incorrect answer, five targeted adversarial passages, and clean Contriever retrieval results. For the reported held-out tables, targets 51-100 are evaluated, giving 50 questions per dataset and per poison-rate cell. Targets 1-50 were used during system development. The project identifies NQ as the development dataset for the final arbitration rule and HotpotQA/MS-MARCO as held-out datasets for that rule; therefore, held-out target IDs should not be interpreted as proof that no design decision used any benchmark dataset.

For a poison rate $p=N/5$, the first $N$ adversarial passages are combined with the clean candidates and ranked using Contriever scores. The top five passages are passed to the system. The tested rates are 0%, 20%, 40%, 60%, 80%, and 100% poisoned passages in the candidate set. All measured systems receive the same question and the same ranked top-five context for each case.

The primary comparison uses the `without_q` poison format, in which the adversarial passage does not repeat the question prefix. A separate `with_q` format prepends the question to the poison and represents the query-optimized format used in the TrustRAG code path. Prompt-injection-passage (PIA) tests, style-diverse/adaptive poisons, knowledge-mimic poisons, and smoke-test jailbreak/PII cases are additional evaluations; their results are not pooled into the primary corpus-poisoning tables.

### 3.1.4 PoisonGuard-RAG v5 Architecture

The implemented package contains eight request-processing stages.

#### Stage 1: Input Normalization

The raw question is repaired for mojibake and common Unicode or formatting obfuscation, including hidden and zero-width characters. Whitespace and contractions are normalized using the shared text-preprocessing utilities. Length status is recorded rather than used as a blocking decision in this benchmarked version. This avoids treating short but legitimate questions as attacks and keeps length handling separate from injection classification.

#### Stage 2: Query-Side Injection Gate

The normalized question is scored with LLM-Guard's ProtectAI DeBERTa-v3 prompt-injection scanner. The resulting injection probability $r_q$ is added to a per-query risk state. A hard block occurs when $r_q \geq 0.90$; lower scores raise risk but do not alone block the query. This gate focuses on instruction injection and is not treated as a detector for fluent false facts.

#### Stage 3: Retrieval and Benchmark Context

In a standalone deployment, PoisonGuard supports BAAI/bge-m3 embeddings with FAISS inner-product search over normalized vectors. However, the TrustRAG head-to-head does not use that retriever: it supplies a precomputed Contriever top-five list to every system. This choice controls retrieval as a confound and makes the benchmark a defense comparison over identical retrieved evidence, rather than a comparison of retrieval models.

#### Stage 4: Context Instruction Filtering

Each retrieved passage is scanned with the same DeBERTa-v3 injection detector. A passage is dropped when its injection score reaches 0.50; the threshold tightens to 0.30 when the accumulated risk $R$ exceeds 0.45. A supersession-cue detector also targets correction- or update-framed instructions. The strongest context signal is added to the shared risk state. This layer targets instructions embedded in documents.

#### Stage 5: Corpus-Poison Consensus Filtering

Because a factual poison may contain no instruction for the injection scanner to detect, a separate filter scores query echo and coordination among passages. Query echo measures longest-common-subsequence overlap between query tokens and the beginning of a passage. Coordination combines BGE-M3 cosine similarity and ROUGE-L similarity for passage pairs. The centers are fixed at cosine 0.85 and ROUGE-L 0.25, taken from the cited TrustRAG methodology rather than tuned on the held-out answers.

For passage $i$, the implementation combines the query-echo term $q_i$ and coordination term $c_i$ using a noisy-OR:

$$r_i = 1 - \left(1 - 0.9\,\sigma\left(\frac{q_i-0.75}{0.05}\right)\right)(1-0.9c_i).$$

Passages with $r_i \geq 0.5$ are removed. The maximum passage risk is fused into the running risk with weight 0.8:

$$R_t = 1 - (1-R_{t-1})(1-w_t r_t).$$

Near-duplicate coordinated passages are assigned to one source group. The arbitration stage can therefore count a group as only one independent witness, limiting the value of repeating a poison. The filter is designed for query-echoing or coordinated retrieval-optimized poisons; diverse, non-echoing false facts remain a limitation.

#### Stage 6: V5 Evidence Arbitration and Answer Generation

The benchmark's `poisonguard_v5` runner enables best-effort answering and v5 arbitration, but does not enable the v3.2 joint-reading fallback. The generator is local Ollama Llama-3.1-8B, configured deterministically (temperature 0, seed 0). The principal decision process is:

1. The model produces a concise closed-book knowledge statement. An extractor converts it to a short answer or `UNKNOWN`.
2. Each surviving passage is read independently, producing a short answer or `INSUFFICIENT`. Isolated reading prevents one passage from steering interpretation of another.
3. Similar answers are clustered after normalization. Exact/containment matches and token-level F1 of at least 0.6 are treated as agreement. Each source group contributes at most one vote, weighted by its recorded passage trust.
4. If the model knows an answer, its internal answer is retained rather than overridden by a lone conflicting passage. If it does not know, two independent passage groups can corroborate an external answer.
5. If isolated evidence is inconclusive, v5 may generate a best-effort answer. When the poison filter has detected or removed a likely poison, the system applies a dropped-passage answer veto: if a surviving answer matches the answer promoted by a removed passage, matching votes are removed and arbitration is repeated. Low-confidence best-effort behavior is recorded rather than represented as a confident evidence vote.
6. For comparison and yes/no questions, v5 decomposes the question into facts about each entity before forming the closed-book comparison. This step targets errors where a one-shot answer conflates entities.

The evidence rule is therefore not simply “always abstain unless two documents agree.” The v5 best-effort path may still produce an answer when arbitration has no corroborated cluster; the system records the low-confidence route, and poison-aware handling limits reliance on a lone passage that agrees with a removed poison. The joint-reading fallback is a separate v3.2 option and is off for the primary v5 table.

#### Stage 7: Output Privacy Filtering

Presidio masks selected personal-data entities such as email addresses, phone numbers, payment cards, social-security numbers, IBANs, IP addresses, passports, and bank identifiers. A deterministic DLP layer checks patterns for cards, API keys, AWS access keys, and bearer tokens. Candidate card numbers are redacted only when they pass Luhn validation. This stage masks sensitive spans and does not act as the primary attack-success judge.

#### Stage 8: Safe Response

The pipeline returns the answer, a transparent abstention when no trustworthy answer is available, or a fixed refusal when the query gate blocks an injection. Output formatting is separate from the benchmark's ACC/ASR scoring.

### 3.1.5 Baselines and Ablation Design

The main measured baselines are Vanilla RAG without a defense, a local reproduction of TrustRAG's two-stage defense, and PoisonGuard v4 as a previous system version. The primary candidate is PoisonGuard v5. Published paper values are included for context only because they use different question samples and inference stacks.

Component ablations remove one feature at a time using `PG_ABLATE` switches:

- `no_arbitration`: replace evidence arbitration with plain generation over filtered passages;
- `no_internal`: disable the model's closed-book answer as an evidence source;
- `no_consensus`: skip the corpus-poison consensus filter;
- `no_decompose`: disable entity-level decomposition for comparison questions;
- `no_lonefix`: disable the v5 dropped-poison-answer veto and associated lone-survivor handling.

The reported ablation cells cover NQ and HotpotQA at selected poison rates, with 50 questions per cell where run. Decomposition and veto ablations are reported for HotpotQA only. Missing cells mean “not run,” not zero. Since this is a one-component-at-a-time design, it estimates conditional changes under the tested configuration but does not identify interactions among components.

### 3.1.6 Evaluation Metrics and Statistical Analysis

The primary scoring rule follows TrustRAG's string-matching evaluation after lowercasing and trimming whitespace and a final period:

- **Accuracy (ACC):** the correct answer is a substring of the generated answer.
- **Attack Success Rate (ASR):** the attacker's incorrect answer is a substring and the correct answer is absent.

A second scorer uses strict whole-word/phrase boundaries for both answers. It reduces accidental substring matches, especially for short answers such as “no” appearing inside “know” or “not.” Both scores are reported on the same generated outputs as a sensitivity check.

The result tables additionally report clean-question accuracy, refusal/abstention rate, latency, poison-passage recall, filter precision, clean-passage retention, answer quality when a poison reaches generation, and which arbitration route produced the response. For paired system comparisons, the same question-rate instances are aligned and discordant outcomes are tested with the two-sided exact McNemar test. Wilson intervals are used where shown. Best-cell formatting is descriptive and should not be interpreted as a significance test.

The fixed 50-attack smoke suite is a separate preliminary evaluation: 13 direct prompt injections, 13 jailbreaks, 12 BIPIA multi-vector attacks, and 12 PII-extraction cases. Direct injection success is manually checked; other attack and harmfulness outcomes use the judge named in the result table; PII is evaluated as actual leakage. No benign controls are included in that suite. A larger three-seed comparison is marked in progress and is not claimed as completed evidence.

### 3.1.7 Reproducibility and Result Interpretation

The main benchmark runner records per-question answers, retrieved and retained passages, detector scores, risk trace, arbitration decision, block/abstention state, errors, and timing. The table generator aggregates those records for the held-out targets. The v5 system uses the same Llama-3.1-8B generator and same Contriever top-five for all controlled systems. Poison rate, question IDs, and poison text variant are stored per row to enable paired rescoring.

On the held-out results, PoisonGuard v5 has mean ACC/ASR of 72.8/5.2 on NQ, 68.4/8.8 on HotpotQA, and 91.2/4.0 on MS-MARCO across the five poisoned rates. Mean latency is 6.0, 6.2, and 4.6 seconds per query respectively. These results are competitive but not uniformly best at every dataset/rate; the ablations show large dataset-specific effects and the system's advantage must be stated with those trade-offs. The additional style-diverse, knowledge-mimic, second-generator, and smoke-test results are reported separately from the main held-out cells.

This methodology is implemented in `poisonguard_rag/` and benchmarked through `trustrag_benchmark/`. The detailed table bundle and ablation values are documented in [the result tables](Claude%20outputs/tables.md) and [the benchmark methodology](POISONGUARD_TABLES_METHODOLOGY.md).