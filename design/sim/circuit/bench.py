"""Runs one deck with parameter overrides through libngspice and returns the RESULT lines as a dict."""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 90   # seconds per deck run; a run that does not finish is recorded as a timeout, never as a pass

RES = re.compile(r"RESULT\s+(\S+)\s*=\s*(\S+)")


def run_deck(path, params=None, tag=None, workdir=None, keep_wave=False):
    text = open(path).read()
    for k, v in (params or {}).items():
        pat = re.compile(r"^(\.param\s+%s\s*=\s*)\S+" % re.escape(k), re.M)
        if not pat.search(text):
            raise KeyError("deck %s has no .param %s" % (path, k))
        text = pat.sub(lambda m: m.group(1) + repr(v) if not isinstance(v, str) else m.group(1) + v, text)
    workdir = workdir or os.path.join(os.path.dirname(os.path.abspath(path)), "run")
    os.makedirs(workdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0] + (("__" + tag) if tag else "")
    wave = os.path.join(workdir, base + ".wave.txt")
    text = text.replace("@WAVE@", wave)
    run_path = os.path.join(workdir, base + ".cir")
    with open(run_path, "w") as f:
        f.write(text)
    log = os.path.join(workdir, base + ".log")
    # one process per run: libngspice cannot be started twice in one process
    try:
        pr = subprocess.run([sys.executable, "-I", os.path.join(HERE, "ngrun.py"), run_path, log], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        pr = None
    lines = open(log).read().splitlines() if os.path.exists(log) else []
    if pr is None:
        lines.append("Error: TIMEOUT after %d s (run recorded as timeout, no result)" % TIMEOUT)
    elif pr.returncode != 0:
        lines.append("Error: ngspice process exit %d %s" % (pr.returncode, pr.stdout.strip()[-300:]))
    out = {}
    errors = []
    for l in lines:
        m = RES.search(l)
        if m:
            name, val = m.group(1), m.group(2)
            try:
                out[name] = float(val)
            except ValueError:
                out[name] = val
        fatal = ("aborted" in l or "Timestep too small" in l or "singular matrix" in l or "TIMEOUT" in l or "ngspice process exit" in l
                 or "could not be simulated" in l or "Transient op failed" in l or "bad node type" in l or "Internal Error" in l)
        if fatal:
            errors.append(l)
        elif ("meas" in l and "failed" in l.lower()) or "no such vector" in l or "no such variable" in l or "invalid" in l:
            # a threshold that was never crossed (or a value computed from one): the rows that need it get no value (a FAIL for that
            # row); the other values of the run stay usable
            out.setdefault("_measfail", []).append(l[-120:])
    if not keep_wave and os.path.exists(wave):
        os.remove(wave)
    return out, errors
