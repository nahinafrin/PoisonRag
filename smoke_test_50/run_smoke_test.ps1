# Smoke test: 4 attack categories, ~12-13 samples each (n=50 total)
# direct prompt injection | jailbreak | multivector (indirect injection conjunctive) | PII leak
# Run from the project root ("TrustRag - Copy") with .venv311 already activated
# and `ollama serve` running (llama-guard3:1b, llama3.2:3b pulled).
#
# v2 fix: default $ErrorActionPreference ("Continue") is used deliberately -- do NOT
# set it to "Stop". Native tools (transformers/spaCy) write informational lines to
# stderr (e.g. "Device set to use cpu"); under ErrorActionPreference=Stop those get
# treated as terminating errors, which silently killed the whole run after step 1 in
# v1. Output is captured with `2>&1 | Out-File -Encoding utf8` so files are UTF8
# (v1 used `*>` which wrote UTF-16 and was unreadable as plain text elsewhere).

$root = Get-Location
Write-Host "=== Smoke test starting in $root ===" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1) Direct prompt injection  (input gate, C3RF fusion)
# ---------------------------------------------------------------------------
Write-Host "`n[1/4] Direct prompt injection (n=13) ..." -ForegroundColor Yellow
Push-Location dataset
python step_03c_fusion_gate.py --eval "../smoke_test_50/prompt_injection_slice.jsonl" --normalize 2>&1 | Out-File -FilePath "../smoke_test_50/results_prompt_injection.txt" -Encoding utf8
Pop-Location
Write-Host "  done -> smoke_test_50/results_prompt_injection.txt"

# ---------------------------------------------------------------------------
# 2) Jailbreak  (input gate, C3RF fusion)
# ---------------------------------------------------------------------------
Write-Host "`n[2/4] Jailbreak (n=13) ..." -ForegroundColor Yellow
Push-Location dataset
python step_03c_fusion_gate.py --eval "../smoke_test_50/jailbreak_slice.jsonl" --normalize 2>&1 | Out-File -FilePath "../smoke_test_50/results_jailbreak.txt" -Encoding utf8
Pop-Location
Write-Host "  done -> smoke_test_50/results_jailbreak.txt"

# ---------------------------------------------------------------------------
# 3) PII leak  (Row 8: full pipeline OFF vs ON, real Ollama generation)
# ---------------------------------------------------------------------------
Write-Host "`n[3/4] PII leak / extraction (n=12) ..." -ForegroundColor Yellow
Push-Location "step4 dataset"
python run_mitigation_ab.py --slice "../smoke_test_50/row8_mitigation_results/row8_pii_extraction.jsonl" --run-dir "../smoke_test_50/row8_mitigation_results/extraction" --limit 12 2>&1 | Out-File -FilePath "../smoke_test_50/results_pii_run.txt" -Encoding utf8
python score_pii_leak.py --slice "../smoke_test_50/row8_mitigation_results/row8_pii_extraction.jsonl" --off "../smoke_test_50/row8_mitigation_results/extraction/off.jsonl" --on "../smoke_test_50/row8_mitigation_results/extraction/on_full.jsonl" --out "../smoke_test_50/row8_mitigation_results/extraction/pii_leak_report.json" 2>&1 | Out-File -FilePath "../smoke_test_50/results_pii_score.txt" -Encoding utf8
Pop-Location
Write-Host "  done -> smoke_test_50/row8_mitigation_results/extraction/pii_leak_report.json"

# ---------------------------------------------------------------------------
# 4) Multivector  (Row 4: query+context conjunctive, real BIPIA attack text)
# ---------------------------------------------------------------------------
Write-Host "`n[4/4] Multivector / indirect injection conjunctive (n=12) ..." -ForegroundColor Yellow
Push-Location "step4 dataset"
python run_mitigation_ab.py --slice "../smoke_test_50/row4_mitigation_results/row4_multivector_conjunctive.jsonl" --run-dir "../smoke_test_50/row4_mitigation_results/conjunctive" --limit 12 2>&1 | Out-File -FilePath "../smoke_test_50/results_multivector_run.txt" -Encoding utf8
python score_row4_detection.py --off "../smoke_test_50/row4_mitigation_results/conjunctive/off.jsonl" --on "../smoke_test_50/row4_mitigation_results/conjunctive/on_full.jsonl" --out "../smoke_test_50/row4_mitigation_results/conjunctive/detection_report.json" 2>&1 | Out-File -FilePath "../smoke_test_50/results_multivector_score.txt" -Encoding utf8
Pop-Location
Write-Host "  done -> smoke_test_50/row4_mitigation_results/conjunctive/detection_report.json"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host "`n=== ALL 4 CATEGORIES COMPLETE ===" -ForegroundColor Green
Write-Host "`n--- Prompt injection (C3RF fused line) ---"
Select-String -Path "smoke_test_50/results_prompt_injection.txt" -Pattern "C3RF"
Write-Host "`n--- Jailbreak (C3RF fused line) ---"
Select-String -Path "smoke_test_50/results_jailbreak.txt" -Pattern "C3RF"
Write-Host "`n--- PII leak report ---"
Get-Content "smoke_test_50/row8_mitigation_results/extraction/pii_leak_report.json"
Write-Host "`n--- Multivector detection report ---"
Get-Content "smoke_test_50/row4_mitigation_results/conjunctive/detection_report.json"

Write-Host "`n=== Smoke test finished ===" -ForegroundColor Cyan
"ALL_DONE" | Out-File -FilePath "smoke_test_50/ALL_DONE.marker" -Encoding utf8
