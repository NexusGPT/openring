import os, datetime, csv
LEDGER = "/work/results/ledger_round2.csv"
def utc(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def ledger(run_id, event, note=""):
    with open(LEDGER, "a") as f: f.write("%s,%s,%s,%s\n" % (run_id, event, utc(), note))
def crossings(f, rl, level=10.0):
    """first frequency below and above the minimum where return loss falls under `level` dB (linear interpolation); None if absent"""
    import numpy as np
    i = int(np.argmax(rl)); lo = hi = None
    for k in range(i, 0, -1):
        if rl[k - 1] < level <= rl[k]: lo = f[k - 1] + (level - rl[k - 1]) / (rl[k] - rl[k - 1]) * (f[k] - f[k - 1]); break
    for k in range(i, len(f) - 1):
        if rl[k + 1] < level <= rl[k]: hi = f[k] + (rl[k] - level) / (rl[k] - rl[k + 1]) * (f[k + 1] - f[k]); break
    return lo, hi
