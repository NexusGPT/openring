import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
p = os.path.join(D, "case-architecture.md")
s = open(p).read()
a = "Check of this version: r4/final_check.log, PASS with 0 failures over 8012 pair checks"
b = "Check of this version (with the corrected pin heights): r4/pins_full_check.log, PASS with 0 failures over 8035 pair checks"
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w").write(s)
print("case-architecture.md: check reference 8012 -> 8035 (r4/pins_full_check.log)")
p = os.path.join(D, "case-model-r4-notes.md")
s = open(p).read()
a = "- Full check of this model: r4/pins_full_check.log (running at the time of writing; exit code in r4/pins_full_check.done)."
b = ("- Full check of this model: r4/pins_full_check.log ends `case_check: PASS, 8035 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]`, exit 0 "
     "(09:18:40 to 10:28:38); lift results unchanged from section 9 (r4/pins_full_check_summary.log); doc check r4/pins_docs.log `RESULT PASS (0 findings)`.")
assert s.count(a) == 1
s = s.replace(a, b)
j = s.rindex("\nRESULT: ")
s = s[:j] + ("\nRESULT: done, both routed boards are in the model, the pins work inside the maker's 1.90 to 2.20 mm (P2 P3 1.980 to 2.118, P1 P4 2.139 to 2.150) "
             "with every pin over its own pad, case_check passes with 8035 pairs and 0 failures at US 7 to 13 including the lift out, and every broken copy fails its test.\n")
open(p, "w").write(s)
print("notes updated")
