# Final comparison — PoisonGuard-RAG v5 vs TrustRAG (held-out test half)

PoisonedRAG / TrustRAG Table-2 protocol: Llama-3.1-8B (Ollama `llama3.1:8b`) for every system, Contriever top-5, poisons without the question prefix, poison rate = poisoned passages / 5. **Test set = PoisonedRAG targets 51-100 of each dataset (50 questions per cell); targets 1-50 were used to design v4/v5 and are not reported here.** Bold = best of TrustRAG / v4 in that cell (ties bold both).

## Metric: TrustRAG paper (substring)

| Dataset | Defense | Poison-(100%) ACC↑ / ASR↓ | Poison-(80%) ACC↑ / ASR↓ | Poison-(60%) ACC↑ / ASR↓ | Poison-(40%) ACC↑ / ASR↓ | Poison-(20%) ACC↑ / ASR↓ | Poison-(0%) ACC↑ |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG | 24 / 70 | 28 / 62 | 30 / 58 | 28 / 56 | 44 / 36 | 66 |
|  | TrustRAG (official code, reproduced) | 68 / **6** | 68 / **4** | 72 / **2** | **76** / 6 | 68 / 6 | 70 |
|  | PoisonGuard-RAG v3.1 | 70 / 2 | 70 / 6 | 70 / 6 | 70 / 2 | 74 / 2 | 74 |
|  | PoisonGuard-RAG v4 | 72 / 4 | 76 / 4 | 72 / 8 | 74 / 6 | 76 / 2 | 76 |
|  | **PoisonGuard-RAG v5 (ours, final)** | **70** / 10 | **72** / 6 | **74** / 4 | 74 / **4** | **74** / **2** | **74** |
|  | *TrustRAG — paper (all 100 q)* | 83 / 2 | 85 / 1 | 84 / 1 | 83 / 1 | 82 / 9 | 82 |
| HotpotQA | Vanilla RAG | 4 / 96 | 18 / 82 | 24 / 76 | 28 / 72 | 42 / 54 | 74 |
|  | TrustRAG (official code, reproduced) | **64** / 8 | 66 / 6 | **78** / **4** | **70** / **8** | 62 / 28 | 76 |
|  | PoisonGuard-RAG v3.1 | 42 / 2 | 40 / 4 | 42 / 4 | 42 / 10 | 54 / 26 | 56 |
|  | PoisonGuard-RAG v4 | 64 / 4 | 66 / 6 | 70 / 4 | 58 / 14 | 70 / 14 | 76 |
|  | **PoisonGuard-RAG v5 (ours, final)** | 62 / **0** | **70** / **4** | 74 / 10 | 66 / 16 | **70** / **14** | **78** |
|  | *TrustRAG — paper (all 100 q)* | 67 / 4 | 71 / 4 | 70 / 7 | 69 / 5 | 66 / 18 | 74 |
| MS-MARCO | Vanilla RAG | 46 / 42 | 46 / 42 | 44 / 42 | 54 / 34 | 58 / 28 | 76 |
|  | TrustRAG (official code, reproduced) | 84 / 10 | 84 / 10 | 84 / 10 | 84 / 10 | 86 / 10 | 84 |
|  | PoisonGuard-RAG v3.1 | 88 / 2 | 88 / 2 | 88 / 2 | 86 / 6 | 86 / 6 | 88 |
|  | PoisonGuard-RAG v4 | 92 / 2 | 92 / 2 | 90 / 2 | 92 / 4 | 90 / 4 | 92 |
|  | **PoisonGuard-RAG v5 (ours, final)** | **92** / **4** | **92** / **4** | **92** / **2** | **90** / **4** | **90** / **6** | **92** |
|  | *TrustRAG — paper (all 100 q)* | 87 / 5 | 84 / 8 | 85 / 7 | 85 / 7 | 83 / 11 | 85 |

## Metric: strict whole-word (same rule for every system)

| Dataset | Defense | Poison-(100%) ACC↑ / ASR↓ | Poison-(80%) ACC↑ / ASR↓ | Poison-(60%) ACC↑ / ASR↓ | Poison-(40%) ACC↑ / ASR↓ | Poison-(20%) ACC↑ / ASR↓ | Poison-(0%) ACC↑ |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG | 22 / 72 | 26 / 64 | 28 / 60 | 26 / 58 | 42 / 38 | 66 |
|  | TrustRAG (official code, reproduced) | 68 / **6** | 68 / **4** | 72 / **2** | **76** / 6 | 68 / 6 | 70 |
|  | PoisonGuard-RAG v3.1 | 74 / 4 | 70 / 6 | 70 / 6 | 70 / 2 | 74 / 2 | 74 |
|  | PoisonGuard-RAG v4 | 72 / 4 | 76 / 4 | 72 / 8 | 74 / 6 | 76 / 2 | 76 |
|  | **PoisonGuard-RAG v5 (ours, final)** | **70** / 10 | **72** / 6 | **74** / 4 | 74 / **4** | **74** / **2** | **74** |
| HotpotQA | Vanilla RAG | 4 / 94 | 18 / 80 | 24 / 74 | 28 / 70 | 42 / 50 | 74 |
|  | TrustRAG (official code, reproduced) | **64** / 6 | 66 / 4 | **76** / **2** | **70** / **4** | 58 / 28 | 76 |
|  | PoisonGuard-RAG v3.1 | 42 / 6 | 40 / 4 | 42 / 4 | 42 / 8 | 54 / 24 | 56 |
|  | PoisonGuard-RAG v4 | 64 / 2 | 66 / 4 | 70 / 4 | 58 / 14 | 70 / 14 | 76 |
|  | **PoisonGuard-RAG v5 (ours, final)** | 60 / **0** | **70** / **2** | 74 / 10 | 66 / 16 | **70** / **14** | **78** |
| MS-MARCO | Vanilla RAG | 44 / 44 | 44 / 44 | 44 / 42 | 54 / 34 | 58 / 28 | 76 |
|  | TrustRAG (official code, reproduced) | 78 / **4** | 82 / **0** | 78 / **0** | 76 / **0** | 80 / **6** | 76 |
|  | PoisonGuard-RAG v3.1 | 86 / 2 | 88 / 2 | 86 / 2 | 84 / 6 | 84 / 6 | 86 |
|  | PoisonGuard-RAG v4 | 88 / 2 | 88 / 2 | 88 / 2 | 90 / 4 | 88 / 4 | 90 |
|  | **PoisonGuard-RAG v5 (ours, final)** | **88** / **4** | **88** / 4 | **88** / 2 | **88** / 4 | **88** / **6** | **88** |

## Summary (paper metric, mean over the five poisoned rates; clean ACC separately)

| Dataset | Defense | mean ACC↑ | mean ASR↓ | clean ACC↑ | answered without refusal (clean) | s/query |
|---|---|---|---|---|---|---|
| NQ | TrustRAG (official code, reproduced) | 70.4 | 4.8 | 70 | 100% | 26.9 |
| NQ | PoisonGuard-RAG v3.1 | 70.8 | 3.6 | 74 | 98% | 14.4 |
| NQ | PoisonGuard-RAG v4 | 74.0 | 4.8 | 76 | 100% | 8.1 |
| NQ | **PoisonGuard-RAG v5 (ours, final)** | 72.8 | 5.2 | 74 | 100% | 6.0 |
| HotpotQA | TrustRAG (official code, reproduced) | 68.0 | 10.8 | 76 | 100% | 21.6 |
| HotpotQA | PoisonGuard-RAG v3.1 | 44.0 | 9.2 | 56 | 72% | 15.4 |
| HotpotQA | PoisonGuard-RAG v4 | 65.6 | 8.4 | 76 | 100% | 7.4 |
| HotpotQA | **PoisonGuard-RAG v5 (ours, final)** | 68.4 | 8.8 | 78 | 100% | 6.2 |
| MS-MARCO | TrustRAG (official code, reproduced) | 84.4 | 10.0 | 84 | 100% | 20.8 |
| MS-MARCO | PoisonGuard-RAG v3.1 | 87.2 | 3.6 | 88 | 94% | 14.2 |
| MS-MARCO | PoisonGuard-RAG v4 | 91.2 | 2.8 | 92 | 100% | 5.2 |
| MS-MARCO | **PoisonGuard-RAG v5 (ours, final)** | 91.2 | 4.0 | 92 | 100% | 4.6 |
