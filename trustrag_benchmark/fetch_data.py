"""Fetch the clean BEIR passages TrustRAG/PoisonedRAG retrieve for the 100 target
queries per dataset, and score the PoisonedRAG adversarial passages with Contriever
(dot product, mean pooling) exactly as TrustRAG's main_trustrag.py does, so poisoned
and clean passages can be merged into one top-k list.

Outputs (data/):
  {ds}_corpus_subset.json   {doc_id: {"title":..., "text":...}}
  {ds}_adv_scores.json      {query_id: {"with_q": [score x5], "without_q": [score x5]}}
"""
import gzip, io, json, os, sys, time
import requests

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATASETS = sys.argv[1:] or ["nq", "hotpotqa", "msmarco"]
needed = json.load(open(os.path.join(DATA, "needed_doc_ids.json")))


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fetch_via_filter(ds, ids):
    out = {}
    base = "https://datasets-server.huggingface.co/filter"
    ids = list(ids)
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        where = '"_id" IN (' + ",".join("'" + x + "'" for x in chunk) + ")"
        for attempt in range(4):
            r = requests.get(base, params={"dataset": f"BeIR/{ds}", "config": "corpus", "split": "corpus",
                                           "where": where, "offset": 0, "length": 100}, timeout=120)
            if r.status_code == 200:
                for row in r.json()["rows"]:
                    rr = row["row"]
                    out[rr["_id"]] = {"title": rr.get("title", ""), "text": rr.get("text", "")}
                break
            time.sleep(3 * (attempt + 1))
        else:
            raise RuntimeError(f"filter API failed: {r.status_code} {r.text[:200]}")
        log(ds, "filter", len(out), "/", len(ids))
    return out


def fetch_via_download(ds, ids):
    from huggingface_hub import HfApi, hf_hub_download
    files = HfApi().list_repo_files(f"BeIR/{ds}", repo_type="dataset")
    log(ds, "repo files:", files)
    cand = [f for f in files if "corpus" in f.lower()]
    if not cand:
        raise RuntimeError(f"no corpus file in BeIR/{ds}: {files}")
    ids = set(ids)
    out = {}
    for f in cand:
        path = hf_hub_download(f"BeIR/{ds}", f, repo_type="dataset")
        log(ds, "downloaded", f, "->", path)
        if f.endswith(".parquet"):
            import pyarrow as pa, pyarrow.compute as pc, pyarrow.parquet as pq
            pf = pq.ParquetFile(path)
            want = pa.array(sorted(ids))
            for batch in pf.iter_batches(batch_size=200_000, columns=["_id", "title", "text"]):
                sel = batch.filter(pc.is_in(batch.column("_id"), value_set=want))
                for rr in sel.to_pylist():
                    out[rr["_id"]] = {"title": rr.get("title", ""), "text": rr.get("text", "")}
        else:
            opener = gzip.open if f.endswith(".gz") else open
            with opener(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    rr = json.loads(line)
                    if rr["_id"] in ids:
                        out[rr["_id"]] = {"title": rr.get("title", ""), "text": rr.get("text", "")}
        if len(out) == len(ids):
            break
    return out


def score_adv(ds):
    import torch
    from transformers import AutoTokenizer, AutoModel
    tok = AutoTokenizer.from_pretrained("facebook/contriever")
    model = AutoModel.from_pretrained("facebook/contriever").eval()

    def emb(texts):
        with torch.no_grad():
            inp = tok(texts, padding=True, truncation=True, return_tensors="pt")
            out = model(**inp).last_hidden_state
            m = inp["attention_mask"].unsqueeze(-1).float()
            return (out * m).sum(1) / m.sum(1)

    targets = json.load(open(os.path.join(DATA, f"{ds}_targets.json")))
    res = {}
    for t in targets:
        q = emb([t["question"]])
        with_q = [t["question"] + "." + a for a in t["adv_texts"]]   # PoisonedRAG LM_targeted (TrustRAG code)
        without_q = list(t["adv_texts"])                               # TrustRAG Table 4 "w/o question"
        s1 = (emb(with_q) @ q.T).squeeze(-1).tolist()
        s2 = (emb(without_q) @ q.T).squeeze(-1).tolist()
        res[t["id"]] = {"with_q": s1, "without_q": s2}
    json.dump(res, open(os.path.join(DATA, f"{ds}_adv_scores.json"), "w"))
    log(ds, "adv scores done")


for ds in DATASETS:
    outp = os.path.join(DATA, f"{ds}_corpus_subset.json")
    if not os.path.exists(outp):
        ids = needed[ds]
        try:
            docs = fetch_via_filter(ds, ids)
        except Exception as e:
            log(ds, "filter API unavailable:", e, "-> downloading corpus")
            docs = fetch_via_download(ds, ids)
        missing = [i for i in ids if i not in docs]
        log(ds, "got", len(docs), "missing", len(missing))
        json.dump(docs, open(outp, "w", encoding="utf-8"))
    if not os.path.exists(os.path.join(DATA, f"{ds}_adv_scores.json")):
        score_adv(ds)
log("ALL DONE")
