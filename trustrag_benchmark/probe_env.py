import json, subprocess, time, platform, os
out = {"platform": platform.platform(), "cpu_count": os.cpu_count()}
try:
    out["nvidia_smi"] = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], capture_output=True, text=True, timeout=20).stdout
except Exception as e:
    out["nvidia_smi"] = f"ERR {e}"
import requests
try:
    out["ollama_tags"] = [m["name"] for m in requests.get("http://localhost:11434/api/tags", timeout=10).json()["models"]]
except Exception as e:
    out["ollama_tags"] = f"ERR {e}"
try:
    t = time.time()
    r = requests.post("http://localhost:11434/api/generate", json={"model": "llama3.2:3b", "prompt": "Answer briefly: what is the capital of France?", "stream": False, "options": {"temperature": 0.01, "num_predict": 64}}, timeout=300).json()
    out["ollama_gen"] = {"text": r.get("response"), "sec": round(time.time() - t, 2), "eval_count": r.get("eval_count"), "eval_duration_s": (r.get("eval_duration") or 0) / 1e9}
except Exception as e:
    out["ollama_gen"] = f"ERR {e}"
try:
    u = 'https://datasets-server.huggingface.co/filter?dataset=BeIR/nq&config=corpus&split=corpus&where="_id"=\'doc0\'&offset=0&length=5'
    r = requests.get(u, timeout=60)
    out["hf_filter"] = {"status": r.status_code, "body": r.text[:600]}
except Exception as e:
    out["hf_filter"] = f"ERR {e}"
try:
    r = requests.get("https://huggingface.co/api/models/facebook/contriever", timeout=30)
    out["hf_hub"] = r.status_code
except Exception as e:
    out["hf_hub"] = f"ERR {e}"
try:
    import rouge_score; out["rouge_score"] = "ok"
except Exception as e:
    out["rouge_score"] = f"missing {e}"
json.dump(out, open("probe_env_result.json", "w"), indent=2)
print(json.dumps(out, indent=2))
