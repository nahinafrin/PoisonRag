import json, time, requests
U = "http://localhost:11434"
out = []
for opts in [{"num_ctx": 4096}, {"num_ctx": 2048}]:
    t = time.time()
    r = requests.post(f"{U}/api/chat", json={"model": "llama3.1:8b", "stream": False, "keep_alive": "60m",
        "messages": [{"role": "user", "content": "Write 150 words about the history of Paris."}],
        "options": dict(temperature=0.01, num_predict=200, seed=0, **opts)}, timeout=600).json()
    out.append({"opts": opts, "wall": round(time.time() - t, 2), "load_s": r.get("load_duration", 0) / 1e9,
                "prompt_tok": r.get("prompt_eval_count"), "prompt_s": r.get("prompt_eval_duration", 0) / 1e9,
                "gen_tok": r.get("eval_count"), "gen_s": r.get("eval_duration", 0) / 1e9})
    out.append({"ps": requests.get(f"{U}/api/ps").json()})
json.dump(out, open("ollama_speed.json", "w"), indent=1)
