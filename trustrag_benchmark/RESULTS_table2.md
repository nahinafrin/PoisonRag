# PoisonGuard-RAG vs TrustRAG — TrustRAG Table 2 protocol

All measured rows: same backbone (Ollama `llama3.1:8b`), same Contriever top-5 passages, same PoisonedRAG poisons, TrustRAG's own ACC/ASR code. **Bold** = best measured defense (complete 100-question cells only). Paper rows are the published Llama-3.1-8B numbers (authors' LMDeploy setup) for reference. NQ was used to design the final arbitration rule (development set); HotpotQA and MS-MARCO are held out.

### Table 2 (paper setting: poisons without the question prefix)

| Dataset | Defense | Poison-(100%) ACC↑ / ASR↓ | Poison-(80%) ACC↑ / ASR↓ | Poison-(60%) ACC↑ / ASR↓ | Poison-(40%) ACC↑ / ASR↓ | Poison-(20%) ACC↑ / ASR↓ | Poison-(0%) ACC↑ |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG | 26.0 / 69.0 | 28.0 / 65.0 | 33.0 / 57.0 | 35.0 / 49.0 | 46.0 / 34.0 | 68.0 |
|  | TrustRAG stage 1&2 (reproduced, official code) | **77.0** / 4.0 | **77.0** / 4.0 | **79.0** / **1.0** | **81.0** / 5.0 | 77.0 / 5.0 | 78.0 |
|  | PoisonGuard-RAG v3.1 (isolated arbitration) | 76.0 / **2.0** | 76.0 / **3.0** | 77.0 / 3.0 | 77.0 / **1.0** | **79.0** / **1.0** | **79.0** |
|  | PoisonGuard-RAG v3.2 (+ joint-reading fallback, final) | – | – | – | – | – | – |
| | *Vanilla RAG — paper* | 2.0 / 98.0 | 2.0 / 98.0 | 3.0 / 97.0 | 4.0 / 93.0 | 26.0 / 73.0 | 71.0 |
| | *TrustRAG stage 1&2 — paper* | 83.0 / 2.0 | 85.0 / 1.0 | 84.0 / 1.0 | 83.0 / 1.0 | 82.0 / 9.0 | 82.0 |
| MS-MARCO | Vanilla RAG | 38.0 / 54.0 | 39.0 / 53.0 | 41.0 / 50.0 | 45.0 / 45.0 | 57.0 / 32.0 | 81.0 |
|  | TrustRAG stage 1&2 (reproduced, official code) | 86.0 / 8.0 | 84.0 / 8.0 | 86.0 / 9.0 | **87.0** / 7.0 | 90.5 / 4.8 (n=21) | – |
|  | PoisonGuard-RAG v3.1 (isolated arbitration) | **87.0** / **3.0** | **87.0** / **4.0** | **87.0** / **4.0** | 86.0 / **6.0** | **87.0** / **5.0** | **88.0** |
|  | PoisonGuard-RAG v3.2 (+ joint-reading fallback, final) | – | – | – | – | – | – |
| | *Vanilla RAG — paper* | 3.0 / 97.0 | 3.0 / 96.0 | 5.0 / 94.0 | 7.0 / 93.0 | 28.0 / 70.0 | 79.0 |
| | *TrustRAG stage 1&2 — paper* | 87.0 / 5.0 | 84.0 / 8.0 | 85.0 / 7.0 | 85.0 / 7.0 | 83.0 / 11.0 | 85.0 |
| HotpotQA | Vanilla RAG | 6.0 / 94.0 | 17.0 / 83.0 | 22.0 / 76.0 | 30.0 / 69.0 | 38.0 / 58.0 | 73.0 |
|  | TrustRAG stage 1&2 (reproduced, official code) | **65.0** / 6.0 | **68.0** / 7.0 | **77.0** / **4.0** | **69.0** / **7.0** | **66.0** / **24.0** | **76.0** |
|  | PoisonGuard-RAG v3.1 (isolated arbitration) | 47.0 / **4.0** | 47.0 / **6.0** | 47.0 / 5.0 | 49.0 / 9.0 | 53.0 / 28.0 | 57.0 |
|  | PoisonGuard-RAG v3.2 (+ joint-reading fallback, final) | – | – | – | – | – | – |
| | *Vanilla RAG — paper* | 1.0 / 99.0 | 2.0 / 97.0 | 6.0 / 94.0 | 5.0 / 94.0 | 27.0 / 81.0 | 71.0 |
| | *TrustRAG stage 1&2 — paper* | 67.0 / 4.0 | 71.0 / 4.0 | 70.0 / 7.0 | 69.0 / 5.0 | 66.0 / 18.0 | 74.0 |

### Supplementary: PoisonedRAG poisons WITH the question prefix (TrustRAG code default)

| Dataset | Defense | Poison-(100%) ACC↑ / ASR↓ | Poison-(80%) ACC↑ / ASR↓ | Poison-(60%) ACC↑ / ASR↓ | Poison-(40%) ACC↑ / ASR↓ | Poison-(20%) ACC↑ / ASR↓ | Poison-(0%) ACC↑ |
|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG | 10.0 / 90.0 | – | – | – | 45.0 / 48.0 | 68.0 |
|  | TrustRAG stage 1&2 (reproduced, official code) | **77.0** / **1.0** | – | – | – | **78.0** / 8.0 | 78.0 |
|  | PoisonGuard-RAG v3.1 (isolated arbitration) | 76.0 / **1.0** | – | – | – | 76.0 / **1.0** | **79.0** |
|  | PoisonGuard-RAG v3.2 (+ joint-reading fallback, final) | – | – | – | – | – | – |
| MS-MARCO | Vanilla RAG | – | – | – | – | – | 81.0 |
|  | TrustRAG stage 1&2 (reproduced, official code) | – | – | – | – | – | – |
|  | PoisonGuard-RAG v3.1 (isolated arbitration) | – | – | – | – | – | **88.0** |
|  | PoisonGuard-RAG v3.2 (+ joint-reading fallback, final) | – | – | – | – | – | – |
| HotpotQA | Vanilla RAG | 4.0 / 96.0 | – | – | – | 43.0 / 53.0 | 73.0 |
|  | TrustRAG stage 1&2 (reproduced, official code) | **68.0** / 5.0 | – | – | – | **67.0** / 21.0 | **76.0** |
|  | PoisonGuard-RAG v3.1 (isolated arbitration) | 47.0 / **2.0** | – | – | – | 49.0 / **2.0** | 57.0 |
|  | PoisonGuard-RAG v3.2 (+ joint-reading fallback, final) | – | – | – | – | – | – |

### Prompt-injection attack (PIA, TrustRAG Table 1 setting: 1 injected passage in top-5)

| Dataset | Defense | ACC↑ / ASR↓ | n |
|---|---|---|---|
| NQ | Vanilla RAG | 45.0 / 43.0 | 100 |
| NQ | TrustRAG stage 1&2 (reproduced, official code) | 78.0 / 4.0 | 100 |
| NQ | PoisonGuard-RAG v3.1 (isolated arbitration) | 77.0 / 5.0 | 100 |
| HotpotQA | Vanilla RAG | 35.0 / 53.0 | 100 |
| HotpotQA | TrustRAG stage 1&2 (reproduced, official code) | 71.0 / 7.0 | 100 |
| HotpotQA | PoisonGuard-RAG v3.1 (isolated arbitration) | 54.0 / 16.0 | 100 |

### Cost and benign refusals (all measured runs)

| Defense | mean s/query | refused or abstained (clean 0% runs) |
|---|---|---|
| Vanilla RAG | 5.1 | 0.0% |
| TrustRAG stage 1&2 (reproduced, official code) | 23.9 | 0.0% |
| PoisonGuard-RAG v3.1 (isolated arbitration) | 15.2 | 11.0% |