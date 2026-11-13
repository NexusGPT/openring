"""Part 2 driver (antenna-sim.md section 12.2 with the correction of 17): runs h1c_standin.py as sub-processes, each capped at 30 minutes."""
import subprocess, json, os, sys
sys.path.insert(0, "/work/src")
import r2_common as R
cands = [(a, vs) for a in (0.7, 0.5) for vs in (0.1, 0.3, 0.5, -0.1, 0.4)]
best = None; n = 0; frozen = None
for (a, vs) in cands:
    eps = 28.9
    for it in range(3):
        n += 1
        if n > 30: break
        tag = "h1c_%02d_a%.1f_v%+.1f" % (n, a, vs)
        try:
            subprocess.run(["timeout", "1800", "python3", "-I", "/work/src/h1c_standin.py", tag, "%.3f" % eps, "%.1f" % a, "%.1f" % vs], check=True, stdout=open("/work/logs/%s.log" % tag, "w"), stderr=subprocess.STDOUT)
            j = json.load(open("/work/results/%s.json" % tag))
        except Exception as e:
            R.ledger(tag, "failed", str(e)[:80]); break
        sc = j["score"]
        print(tag, eps, json.dumps(sc), flush=True)
        if best is None or sc["shortfall"] < best[0]["shortfall"]: best = (sc, tag, eps, a, vs)
        if sc["pass_all"]: frozen = (tag, eps, a, vs); break
        new = min(60.0, max(8.0, eps * (sc["f_min_GHz"] / 2.45) ** 2))
        if abs(new - eps) < 0.05: break
        eps = new
    if frozen or n > 30: break
json.dump(dict(frozen=frozen, best=best, runs=n), open("/work/results/h1c_driver.json", "w"), indent=1)
print("DRIVER DONE", json.dumps(dict(frozen=frozen, best=best, runs=n)))
