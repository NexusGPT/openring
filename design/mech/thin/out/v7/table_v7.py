"""Per-size table of the v7 fit checks, from the logs (one row per size)."""
import re
D = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin/out/v7/")
rows = [("default US 9", "check_us9_default_v7.log")] + [(f"US {n}", f"size_us{n}_v7.log") for n in range(7, 14)]
def g(t, pat, k=1):
    m = re.search(pat, t)
    return m.group(k) if m else "?"
print("| Size | Result line | Joystick | Frame bore / outer / top over surface | Cap top heights 0 / 0.7 / 1.3 / 1.6 / 1.9 over the frame | Cap top to the exterior's | Opening metal X / bottom | Motor rim | Cell | Light parts / board / foam / glass column |")
print("|---|---|---|---|---|---|---|---|---|---|")
for lab, f in rows:
    t = open(D + f).read()
    res = g(t, r"^(RESULT .*)$".replace("^", "(?m)^"))
    joy = g(t, r"joystick opening at (-?[\d.]+) deg")
    fr = g(t, r"bore dia ([\d.]+) \(along X\).*outer dia ([\d.]+), top ([\d.]+) above", 0)
    fr = re.findall(r"bore dia ([\d.]+) \(along X\).*?outer dia ([\d.]+), top ([\d.]+) above", t)
    caps = re.findall(r"joystick cap top at radius [\d.]+ \(\+X\): ([\d.]+) above", t)
    ext = g(t, r"exterior's joystick top r [\d.]+: difference ([+-][\d.]+)")
    om = g(t, r"metal beside it along X \(([\d.]+), [\d.]+\), along the band \(([\d.]+), ([\d.]+)\)", 0)
    om = re.findall(r"metal beside it along X \(([\d.]+), [\d.]+\), along the band \(([\d.]+), ([\d.]+)\)", t)
    rim = g(t, r"motor rim: least metal along the outward ray ([\d.]+)")
    cell = re.findall(r"cell: start .*?, ([\d.]+) mm on r .*?, ([\d.]+) to ([\d.]+) mAh", t)
    lt = re.findall(r"light part: (\[.*?\]); board solid at the old hole (\w+); foam solid there (\w+); glass column there (\d+ of \d+)", t)
    print(f"| {lab} | {res} | {joy} | {'/'.join(fr[0]) if fr else '?'} | {' / '.join(caps) if caps else '?'} | {ext} | "
          f"{(om[0][0] + ' / ' + om[0][2]) if om else '?'} | {rim} | {(cell[0][0] + ' mm, ' + cell[0][1] + ' to ' + cell[0][2] + ' mAh') if cell else '?'} | "
          f"{(' / '.join(lt[0])) if lt else '?'} |")
