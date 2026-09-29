# Extra evaluations (held-out targets 51-100) - interim 2026-09-27 22:50 UTC

Format: ACC/ASR (strict ACC/ASR). n=k means incomplete.

```
== PIA (ACC/ASR, strict in brackets), test 51-100
nq vanilla: 44/44 (44/44) | trustrag: 70/4 (70/4) | poisonguard: 72/8 (72/8) | poisonguard_v5: 70/8 (68/8)
hotpotqa vanilla: 38/52 (38/52) | trustrag: 66/8 (66/8) | poisonguard: 50/16 (50/16) | poisonguard_v5: 54/12 (54/12)
msmarco vanilla: 32/60 (30/62) | trustrag: 82/12 (70/6) | poisonguard: n=0 | poisonguard_v5: 88/4 (84/4)
== adaptive
 nq p5: vanilla: 26/66 (24/68) | trustrag: 70/10 (70/10) | poisonguard_v5: 72/4 (72/4)
 nq p3: vanilla: 30/54 (28/56) | trustrag: n=0 | poisonguard_v5: 74/6 (74/6)
 nq p1: vanilla: 52/30 (52/30) | trustrag: n=0 | poisonguard_v5: 74/4 (74/4)
 hotpotqa p5: vanilla: 6/92 (6/90) | trustrag: 68/10 (68/8) | poisonguard_v5: 56/10 (56/8)
 hotpotqa p3: vanilla: 28/70 (26/68) | trustrag: n=0 | poisonguard_v5: 54/30 (54/28)
 hotpotqa p1: vanilla: 38/58 (38/56) | trustrag: n=0 | poisonguard_v5: 68/20 (68/18)
 msmarco p5: vanilla: 40/48 (40/48) | trustrag: 80/14 (72/6) | poisonguard_v5: 90/6 (86/4)
 msmarco p3: vanilla: 40/48 (38/48) | trustrag: n=0 | poisonguard_v5: 92/2 (86/2)
 msmarco p1: vanilla: 54/34 (54/34) | trustrag: n=0 | poisonguard_v5: 92/4 (86/4)
== mimic
 nq p5: vanilla: 38/52 (36/54) | trustrag: n=0 | poisonguard_v5: 72/4 (72/4)
 nq p3: vanilla: 42/48 (40/50) | trustrag: n=0 | poisonguard_v5: 74/2 (74/2)
 nq p1: vanilla: n=31 | trustrag: n=0 | poisonguard_v5: 72/4 (72/4)
 hotpotqa p5: vanilla: n=0 | trustrag: n=0 | poisonguard_v5: n=0
 hotpotqa p3: vanilla: n=0 | trustrag: n=0 | poisonguard_v5: n=0
 hotpotqa p1: vanilla: n=0 | trustrag: n=0 | poisonguard_v5: n=0
 msmarco p5: vanilla: n=0 | trustrag: n=0 | poisonguard_v5: n=0
 msmarco p3: vanilla: n=0 | trustrag: n=0 | poisonguard_v5: n=0
 msmarco p1: vanilla: n=0 | trustrag: n=0 | poisonguard_v5: n=0
== ablations (test)
 nq p5: full: 70/10 (70/10) | no_arbitration: 40/40 (40/40) | no_internal: 60/18 (60/18) | no_consensus: 70/10 (70/10)
 nq p3: full: 74/4 (74/4) | no_arbitration: 40/40 (40/40) | no_internal: 60/20 (60/20) | no_consensus: 70/10 (70/10)
 nq p1: full: 74/2 (74/2) | no_arbitration: 46/34 (44/36) | no_internal: 70/6 (70/6) | no_consensus: 74/4 (74/4)
 hotpotqa p5: full: 62/0 (60/0) | no_arbitration: 36/32 (36/30) | no_internal: 54/8 (54/4) | no_consensus: 36/56 (36/54) | no_decompose: 66/4 (66/0) | no_lonefix: 62/8 (62/6)
 hotpotqa p3: full: 74/10 (74/10) | no_arbitration: 66/22 (66/20) | no_internal: 74/10 (74/8) | no_consensus: 36/56 (36/54) | no_decompose: 74/6 (74/6) | no_lonefix: 60/10 (60/8)
 hotpotqa p1: full: 70/14 (70/14) | no_arbitration: 46/50 (46/46) | no_internal: 66/20 (66/18) | no_consensus: 70/14 (70/12) | no_decompose: 70/16 (70/16) | no_lonefix: 70/14 (70/12)
```

## Mistral-Nemo-12B (held-out 51-100, ACC/ASR, paper metric) vs TrustRAG paper's own Mistral-Nemo numbers (100 q, appendix tables)

| Dataset | System | 100% | 80% | 60% | 40% | 20% | clean | closed book |
|---|---|---|---|---|---|---|---|---|
| NQ | Vanilla RAG (ours, measured) | 20/66 | - | 20/62 | - | 46/28 | 58 | 46 |
| NQ | TrustRAG (paper, reported) | 64/1 | 64/2 | 63/2 | 65/1 | 67/11 | 69 | |
| NQ | **PoisonGuard-RAG v5 (measured)** | 52/6 | 56/6 | 56/6 | 56/4 | 56/4 | 54 | |
| HotpotQA | Vanilla RAG | 0/98 | - | 10/90 | - | 34/66 | 78 | 64 |
| HotpotQA | TrustRAG (paper, reported) | 75/4 | 79/4 | 79/4 | 78/3 | 74/13 | 78 | |
| HotpotQA | **PoisonGuard-RAG v5** | 68/4 | 78/6 | 82/4 | 80/4 | 82/4 | 80 | |
| MS-MARCO | Vanilla RAG | 50/42 | - | 56/36 | - | 68/22 | 82 | 74 |
| MS-MARCO | TrustRAG (paper, reported) | 85/4 | 84/6 | 83/5 | 82/6 | 84/12 | 82 | |
| MS-MARCO | **PoisonGuard-RAG v5** | 86/2 | 86/2 | 86/2 | 86/2 | 88/0 | 88 | |

PoisonGuard-RAG with Mistral-Nemo: ~6-7 s/query. TrustRAG was not re-run on Mistral-Nemo (paper numbers, different 100-question set) - indicative only.
