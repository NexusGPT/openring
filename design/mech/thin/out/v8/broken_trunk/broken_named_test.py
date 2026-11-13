"""Runs the named test of check_thin.py (check_band_circuits) on the model built from THIS folder's thin.py (a broken copy). No other test, no pair test.
Prints the findings of the named test and a last line RESULT FAIL (findings) or RESULT PASS. Usage: python broken_named_test.py (run from anywhere; the folder of this file is used)."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
import thin
import check_thin
m = thin.build()
parts = m["parts"]
by = {p.name: p for p in parts}
solids = {p.name: p.solids() for p in parts}
f = check_thin.check_band_circuits(thin, m, parts, by, solids, m["ctx"])
for x in f:
    print(x)
print(f"named test findings: {len(f)}")
print("RESULT FAIL" if f else "RESULT PASS")
sys.exit(1 if f else 0)
