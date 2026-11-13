"""fix1 (recorder): every broken copy edit of the units whose files fix round 1 changes must still match exactly once.
Runs each unit's own broken_edit.py on a fresh copy of its module (in this output folder) and prints one line per variant.
Usage: python3 -B -I fix1-rec-editcheck.py <firmware folder> <work folder>"""
import pathlib
import re
import shutil
import subprocess
import sys

fw = pathlib.Path(sys.argv[1])
work = pathlib.Path(sys.argv[2])
units = {
    "recorder": ("ring_recorder", None),
    "store": ("ring_store", "VARIANTS"),
    "xfer": ("ring_xfer", "VARIANTS"),
    "audio": ("ring_audio", "VARIANTS"),
    "motor": ("ring_motor", "VARIANTS"),
}
bad = 0
total = 0
for unit, (mod, var) in units.items():
    ed = fw / "tests" / unit / "broken_edit.py"
    if var is None:
        out = subprocess.run([sys.executable, "-B", "-I", str(ed), "--list"], capture_output=True, text=True)
        variants = out.stdout.split()
    else:
        txt = (fw / "tests" / unit / "broken_run.sh").read_text()
        m = re.search(r'^VARIANTS="([^"]*)"', txt, re.M)
        variants = m.group(1).split()
    for v in variants:
        total += 1
        d = work / f"{unit}-{v}"
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(fw / "modules" / mod, d)
        r = subprocess.run([sys.executable, "-B", "-I", str(ed), v, str(d)], capture_output=True, text=True)
        ok = r.returncode == 0
        bad += 0 if ok else 1
        print(f"{unit} {v}: exit {r.returncode} {'MATCHED ONCE' if ok else 'NO MATCH'} {r.stdout.strip()} {r.stderr.strip()}")
# the devices copy is a sed on rdev_logic.c (fix round 1 does not change that file): count its pattern
dl = (fw / "modules/ring_devices/src/rdev_logic.c").read_text().count("return RDEV_SWITCH_REFUSE_EMPTY;")
total += 1
bad += 0 if dl >= 1 else 1
print(f"devices sed pattern 'return RDEV_SWITCH_REFUSE_EMPTY;' occurrences: {dl}")
print(f"EDITCHECK {total} variants, {bad} not matching")
