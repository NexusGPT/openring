#!/usr/bin/env python3
"""Run only the v9 named tests of check_thin.py (section 14: check_board_plan and check_zone) on the thin.py of folder arg 1, with the check file arg 2.
The thin.py of arg 1 is imported first, so the check's own `import thin` takes it. Prints the tests' lines, the findings, and 'RESULT PASS' or
'RESULT FAIL'; exit 0 / 1. Used for the broken copies (the full check with the pair test is the real run)."""
import importlib.util, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import thin  # noqa: E402
print(f"thin.py: {thin.__file__}; check: {sys.argv[2]}")
spec = importlib.util.spec_from_file_location("check_thin_v9", sys.argv[2])
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)
assert ct.thin is thin
m = thin.build()
P, ctx = m["parts"], m["ctx"]
by = {p.name: p for p in P}
solids = {p.name: p.solids() for p in P}
f = ct.check_board_plan(thin, P, by, solids, ctx) + ct.check_zone(thin, P, by, solids, ctx)
for x in f:
    print(x)
print(f"named test findings: {len(f)}")
print("RESULT " + ("FAIL" if f else "PASS"))
sys.exit(1 if f else 0)
