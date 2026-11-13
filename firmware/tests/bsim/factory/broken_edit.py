"""Edits for tests/bsim/factory/run.sh --broken. Usage: python3 broken_edit.py <variant> <modules folder> <out folder>
Copies modules/ring_factory to <out>/ring_factory, makes the one named fault (the edit must match exactly once) and prints
  MODULE=ring_factory
  EXPECT=<regular expression of the scanner's check line that must say FAIL>
The variants: connectable (the ship beacon can be connected to), never_stops (the beacon is not stopped before the ship
task)."""
import pathlib
import shutil
import sys

V = {
    "connectable": ("src/rfa.c", "return beacon_start(false); /* ship */", "return beacon_start(true); /* ship */",
                    "HOST CHECK every report is not connectable.* FAIL"),
    "never_stops": ("src/rfa.c", "void rfa_beacon_stop(void)\n{\n\tbeacon_stop_now();\n}",
                    "void rfa_beacon_stop(void)\n{\n}",
                    "HOST CHECK stopped within 1 s of VBUS removal.* FAIL"),
}
v, mods, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
rel, old, new, expect = V[v]
dst = out / "ring_factory"
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(mods / "ring_factory", dst)
f = dst / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print("MODULE=ring_factory")
print(f"EXPECT={expect}")
