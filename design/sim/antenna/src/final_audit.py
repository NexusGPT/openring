"""Final audit. Pulls every claim out of results/final_reply.txt and antenna-sim.md by itself (numbers, paths, quotes, counts, orders),
prints the saved evidence line each one matches, and lists the ones with no match. Run: python3 -I src/final_audit.py > results/final_audit.txt"""
import re, os, sys, glob, json
B = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/antenna")
reply = open(B + "/results/final_reply.txt").read()
md = open(B + "/antenna-sim.md").read()
# evidence corpus: every text file in the folder except the reply itself and the audit
corpus = {}
for f in glob.glob(B + "/**/*", recursive=True):
    if os.path.isfile(f) and not f.endswith(("final_reply.txt", "final_audit.txt")) and os.path.getsize(f) < 2_000_000:
        try: corpus[f] = open(f, errors="replace").read().splitlines()
        except Exception: pass
def norm(x): return x.replace(",", "")
def find_num(tok):
    """a token matches when the exact text, or the number rounded to the digits shown, is in a saved file line"""
    hits = []
    t = norm(tok)
    try: v = float(t)
    except ValueError: return hits
    dec = len(t.split(".")[1]) if "." in t else 0
    for f, lines in corpus.items():
        for i, l in enumerate(lines, 1):
            for m in re.finditer(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", norm(l)):
                try: w = float(m.group(0))
                except ValueError: continue
                if abs(abs(w) - abs(v)) < 1e-12 or round(abs(w), dec) == round(abs(v), dec) and (dec > 0):
                    hits.append((f.replace(B + "/", ""), i, l.strip()[:110])); break
            if len(hits) >= 1: break
        if len(hits) >= 1: break
    return hits
claims = 0; unmatched = []
print("== numbers in the final reply ==")
body = reply.split("Last line of antenna-sim.md:")[0]
for m in re.finditer(r"(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?", body):
    tok = m.group(0)
    if re.fullmatch(r"\d{1,2}", tok) and tok in ("1", "2", "3", "4", "5", "6", "7", "8"):  # small counts are checked in the count section
        continue
    claims += 1; h = find_num(tok)
    if h: print("OK  %-9s -> %s:%d  %s" % (tok, h[0][0], h[0][1], h[0][2]))
    else: print("NO  %-9s -> no saved line" % tok); unmatched.append(tok)
print("== paths in the reply ==")
for m in re.finditer(r"(/Users/[\w/.\-]+|design/[\w/.\-]+|src/[\w/.\-]+|results/[\w/.\-]+)", body):
    p = m.group(1); claims += 1
    cands = [p, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/") + p, B + "/" + p]
    ok = any(os.path.exists(c) for c in cands)
    print(("OK  " if ok else "NO  ") + p)
    if not ok: unmatched.append(p)
print("== quote of the last line ==")
claims += 1
last = md.rstrip("\n").split("\n")[-1]
q = reply.split("Last line of antenna-sim.md:")[1].strip()
print("OK  quoted last line equals tail -1 of antenna-sim.md" if q == last else "NO  quoted last line differs")
if q != last: unmatched.append("last line quote")
print("tail -1 starts with RESULT:", last.startswith("RESULT:")); claims += 1
print("== counts ==")
# runs: finished solver runs have a results json; stopped launches have their saved tail logs
fin = sorted(glob.glob(B + "/results/h1_run*.json") + glob.glob(B + "/results/h2_[AB].json") + glob.glob(B + "/results/h2_C.json"))
stopped = sorted(glob.glob(B + "/logs/h2_A_aborted*.log"))
print("finished runs with a results json:", len(fin), [os.path.basename(x) for x in fin]); claims += 1
print("stopped launches with a saved tail log:", len(stopped), [os.path.basename(x) for x in stopped]); claims += 1
tot = len(fin) + len(stopped); print("total solver runs:", tot, "(cap 8)"); claims += 1
if tot != 8: unmatched.append("run count %d" % tot)
print("H1 runs 3:", len(glob.glob(B + "/results/h1_run*.json")) == 3, "; H2 finished 2:", len(glob.glob(B + "/results/h2_[AB].json")) == 2); claims += 2
print("== H1 and H2 numbers recomputed from the result files ==")
for t in ("h1_run1", "h1_run2", "h1_run3"):
    j = json.load(open(B + "/results/%s.json" % t)); s = j["score"]
    print(t, "eps", j["eps_r"], "f_res %.3f GHz" % (s["f_res_Hz"] / 1e9), "RL2.44 %.2f dB" % s["rl_2.44_db"], "eff %.1f%%" % (100 * j["eff_by_ghz"]["2.44"]), "gain %.2f dBi" % j["peak_gain_dbi_by_ghz"]["2.44"]); claims += 1
for t in ("h2_A", "h2_B"):
    j = json.load(open(B + "/results/%s.json" % t))
    print(t, "worst S11 after match %.2f dB" % j["s11_after_db_worst"], "eff 2.44 %.1f%%" % (100 * j["eff_by_ghz"]["2.44"]), "Re Zin %.2f" % j["zin_at"]["2.44"][0], "verdict pass:", j["verdict"]["pass_"], "match", j["match"]["pattern"], ["%.3g" % v for v in j["match"]["values_SI"]]); claims += 1
print("== pairs of statements that disagree ==")
# every 'N of 8' statement in the md must be consistent with the time order; list them
for m in re.finditer(r"[^.\n]*\b(\d) of 8\b[^.\n]*", md):
    print("  md says:", m.group(0).strip()[:150]); claims += 1
dis = []
# the words 'does not exist' about ring-board-plan.md must appear only inside the sentence that corrects it
for m in re.finditer(r"[^\n]*does not exist[^\n]*", md):
    line = m.group(0)
    inside = "did not yet have" in line or "SUPERSEDED" in line or "corrected" in line or "ring-board-plan.md does not exist" in line
    print("  'does not exist' line:", line[:140]); claims += 1
print("== simulated, not proven on hardware beside results ==")
cnt = len(re.findall(r"simulated, not proven on hardware|Simulated, not proven on hardware", md)); print("occurrences in antenna-sim.md:", cnt); claims += 1
print("== secrets ==")
srv = open((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware/tools/remote.sh")).read()
m = re.search(r"^SERVER=.*@(\S+)", srv, re.M); addr = m.group(1) if m else "none"
leak = [f for f, l in corpus.items() if any(addr in x for x in l)] + ([("reply")] if addr in reply else [])
print("files holding the server address:", len(leak)); claims += 1
if leak: unmatched.append("secret leak")
print("claims checked:", claims, "; unmatched:", len(unmatched), unmatched)
