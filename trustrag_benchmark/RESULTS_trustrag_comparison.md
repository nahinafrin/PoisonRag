# TrustRAG head-to-head (PoisonedRAG protocol, Contriever top-5, backbone llama3.1:8b)

## NQ — poisoned passages = question + adv text (TrustRAG code)

| System | Poison 100% ACC↑/ASR↓ | Poison 20% ACC↑/ASR↓ | Poison 0% ACC↑/ASR↓ |
|---|---|---|---|
| Vanilla RAG | 10 / 90 (n=100) | 45 / 48 (n=100) | 68 / – (n=100) |
| TrustRAG (reproduced) | 77 / 1 (n=100) | 78 / 8 (n=100) | 78 / – (n=100) |
| **PoisonGuard-RAG (final)** | 76 / 1 (n=100) | 78 / 1 (n=100) | 79 / – (n=100) |
| Ours v1 (thesis pipeline as locked) | 0 / 0 (n=1) | – | – |
| Ours v2 (+6b poison risk, +9d arbitration) | 60 / 1 (n=100) | 61 / 2 (n=100) | 64 / – (n=100) |
| Ours v2.1 (v2 + reasoned internal knowledge in 9d) | 69 / 1 (n=100) | 66 / 1 (n=100) | 66 / – (n=100) |
| *Vanilla RAG — paper (Llama-3.1-8B)* | 2 / 98 | 26 / 73 | 71 / – |
| *TrustRAG — paper (Llama-3.1-8B)* | 83 / 2 | 82 / 9 | 82 / – |

## NQ — poisoned passages without question prefix

| System | Poison 100% ACC↑/ASR↓ | Poison 80% ACC↑/ASR↓ | Poison 60% ACC↑/ASR↓ | Poison 40% ACC↑/ASR↓ | Poison 20% ACC↑/ASR↓ |
|---|---|---|---|---|---|
| Vanilla RAG | 26 / 69 (n=100) | 28 / 65 (n=100) | 33 / 57 (n=100) | 35 / 49 (n=100) | 46 / 34 (n=100) |
| TrustRAG (reproduced) | 77 / 4 (n=100) | 77 / 4 (n=100) | 79 / 1 (n=100) | 81 / 5 (n=100) | 77 / 5 (n=100) |
| **PoisonGuard-RAG (final)** | 78 / 3 (n=100) | – | – | – | 79 / 1 (n=100) |
| Ours v2 (+6b poison risk, +9d arbitration) | 52 / 16 (n=100) | – | – | – | 60 / 5 (n=100) |
| Ours v2.1 (v2 + reasoned internal knowledge in 9d) | 53 / 18 (n=100) | – | – | – | 63 / 3 (n=100) |

## NQ — poisoned passages PIA prompt-injection attack (1 of 5 passages)

| System | Poison 20% ACC↑/ASR↓ |
|---|---|
| Vanilla RAG | 45 / 43 (n=100) |
| TrustRAG (reproduced) | 78 / 4 (n=100) |
| **PoisonGuard-RAG (final)** | 77 / 5 (n=100) |

## HOTPOTQA — poisoned passages = question + adv text (TrustRAG code)

| System | Poison 100% ACC↑/ASR↓ | Poison 20% ACC↑/ASR↓ | Poison 0% ACC↑/ASR↓ |
|---|---|---|---|
| Vanilla RAG | 4 / 96 (n=100) | 43 / 53 (n=100) | 73 / – (n=100) |
| TrustRAG (reproduced) | 68 / 5 (n=100) | 67 / 21 (n=100) | 76 / – (n=100) |
| **PoisonGuard-RAG (final)** | 47 / 2 (n=100) | 49 / 2 (n=100) | 57 / – (n=100) |
| *Vanilla RAG — paper (Llama-3.1-8B)* | 1 / 99 | 27 / 81 | 71 / – |
| *TrustRAG — paper (Llama-3.1-8B)* | 67 / 4 | 66 / 18 | 74 / – |

## HOTPOTQA — poisoned passages without question prefix

| System | Poison 100% ACC↑/ASR↓ | Poison 80% ACC↑/ASR↓ | Poison 60% ACC↑/ASR↓ | Poison 40% ACC↑/ASR↓ | Poison 20% ACC↑/ASR↓ |
|---|---|---|---|---|---|
| Vanilla RAG | 6 / 94 (n=100) | 17 / 83 (n=100) | 22 / 76 (n=100) | 30 / 69 (n=100) | 38 / 58 (n=100) |
| TrustRAG (reproduced) | 65 / 6 (n=100) | 78 / 17 (n=18) | – | – | 66 / 24 (n=100) |
| **PoisonGuard-RAG (final)** | 48 / 10 (n=100) | – | – | – | 54 / 30 (n=100) |

## HOTPOTQA — poisoned passages PIA prompt-injection attack (1 of 5 passages)

| System | Poison 20% ACC↑/ASR↓ |
|---|---|
| Vanilla RAG | 35 / 53 (n=100) |
| TrustRAG (reproduced) | 71 / 7 (n=100) |
| **PoisonGuard-RAG (final)** | 54 / 16 (n=100) |
