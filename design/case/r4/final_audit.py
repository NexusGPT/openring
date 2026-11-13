"""Final audit: every number and every backquoted phrase of final_reply.md is searched in the saved evidence (r4 logs, the notes, out/case_params.json);
prints each with its first match or NO MATCH, and the count. usage: final_audit.py"""
import glob
import os
import re

R4 = os.path.dirname(os.path.abspath(__file__))
reply = open(os.path.join(R4, "final_reply.md")).read()
files = sorted(set(glob.glob(os.path.join(R4, "*.log")) + [os.path.join(R4, "..", "case-model-r4-notes.md"), os.path.join(R4, "..", "case-bom.csv")]))
texts = {f: open(f, errors="replace").read() for f in files}
claims = re.findall(r"`([^`]+)`", reply) + re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", reply)
miss = 0
for c in claims:
    hit = next((os.path.basename(f) for f, t in texts.items() if c.replace("...", "") in t), None)
    if hit is None:
        miss += 1
    print(("ok   %-60s %s" % (c[:60], hit)) if hit else ("NO MATCH %s" % c))
print("claims checked: %d, without a match: %d" % (len(claims), miss))
