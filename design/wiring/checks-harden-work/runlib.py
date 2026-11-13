import json, os, re, subprocess, sys
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = ROOT + "/design/wiring/checks-harden-work"
PY = ROOT + "/design/.venv/bin/python"
def run_cases(section, cmd_of, manifest, logdir):
    """Runs each case through the real entry point (cmd_of(case) -> argv), at nice 19, one at a time. A case passes when the exit code is
    the wanted one AND (for a wanted failure with a tag) a FAIL[tag] line names the wanted row id. Returns (n_ok, n)."""
    os.makedirs(logdir, exist_ok=True)
    ok = 0
    for c in manifest:
        r = subprocess.run(["nice", "-n", "19"] + cmd_of(c), capture_output=True, text=True)
        out = r.stdout + "\n" + r.stderr
        out = "\n".join(l for l in out.splitlines() if "Debug: Adding duplicate image handler" not in l and "wxApp" not in l)
        open(os.path.join(logdir, c["name"] + ".log"), "w").write(out + "\nEXIT %d\n" % r.returncode)
        got = 0 if r.returncode == 0 else 1
        good = got == c["want_exit"]
        why = ""
        line = ""
        if good and c.get("want_tag"):
            tag = c["want_tag"] if (re.match(r"[A-Z]\d", c["want_tag"]) or re.match(r"[A-Z]\d \w", c["want_tag"])) else "FAIL[%s]" % c["want_tag"]
            hits = [l for l in out.splitlines() if tag in l and (not c.get("want_id") or c["want_id"] in l)]
            if not hits:
                good, why = False, "no %s line naming %s" % (tag, c.get("want_id"))
            else:
                line = hits[0][:200]
        elif good and c["want_exit"] == 1:
            line = next((l for l in out.splitlines() if l.startswith("FAIL")), "")[:200]
        if not good and not why:
            why = "want exit %d got %d" % (c["want_exit"], r.returncode)
        ok += good
        print("CASE %s/%-28s want_exit=%d got_exit=%d %s%s | %s" % (section, c["name"], c["want_exit"], r.returncode,
              "as expected" if good else "DIFFERS (" + why + ")", "", line), flush=True)
    return ok, len(manifest)
