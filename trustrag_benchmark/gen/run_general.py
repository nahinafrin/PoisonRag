"""Orchestrates the generalization run with an 8-hour hard budget (build + all systems).
Seeds run one at a time, each complete across all systems, so a stop never leaves half a seed.
Before starting a seed, the measured duration of the previous seed is used to decide whether it fits."""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
BUDGET = 8 * 3600
T0 = time.time()
LOG = os.path.join(HERE, "general.log")
env = dict(os.environ, BENCH_RESULTS="results_general", PYTHONIOENCODING="utf-8")
env.pop("BENCH_BACKBONE", None); env.pop("PG_ABLATE", None)
DS = ["triviaqa", "twowiki", "squad"]


def log(*a):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + " ".join(map(str, a)) + "\n")


def run(args, extra=None):
    with open(LOG, "a", encoding="utf-8") as f:
        subprocess.run([PY] + args, cwd=HERE, env=dict(env, **(extra or {})), stdout=f, stderr=subprocess.STDOUT)


log("START budget 8h")
seed_time = None
for seed in (1, 2, 3):
    el = time.time() - T0
    need = (seed_time or 0) * 1.1
    if el + need > BUDGET or el > BUDGET:
        log(f"STOP before seed {seed}: elapsed {el/3600:.2f}h, next seed needs ~{need/3600:.2f}h"); break
    ts = time.time()
    run(["gen/build_general.py"], {"GEN_SEEDS": str(seed)})
    for d in DS:
        ds = f"{d}_s{seed}"
        if not os.path.exists(os.path.join(HERE, "data", f"{ds}_adv_scores.json")):
            log("missing data for", ds); continue
        run(["run_final.py", "--system", "poisonguard_v5", "--ds", ds, "--poison", "5", "2", "--variant", "without_q"])
        run(["run_final.py", "--system", "poisonguard_v5", "--ds", ds, "--poison", "0", "--variant", "with_q"])
        run(["baselines.py", "--system", "vanilla", "--ds", ds, "--poison", "5", "2", "--variant", "without_q"])
        run(["baselines.py", "--system", "vanilla", "--ds", ds, "--poison", "0", "--variant", "with_q"])
        run(["baselines.py", "--system", "closedbook", "--ds", ds, "--poison", "0", "--variant", "with_q"])
    for d in DS:
        ds = f"{d}_s{seed}"
        if time.time() - T0 > BUDGET:
            log("STOP inside seed", seed, "(TrustRAG) - budget reached"); break
        run(["baselines.py", "--system", "trustrag", "--ds", ds, "--poison", "5", "2", "--variant", "without_q"])
        run(["baselines.py", "--system", "trustrag", "--ds", ds, "--poison", "0", "--variant", "with_q"])
    seed_time = time.time() - ts
    log(f"seed {seed} done in {seed_time/3600:.2f}h, total {(time.time()-T0)/3600:.2f}h")
log("END", f"{(time.time()-T0)/3600:.2f}h")
