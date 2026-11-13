"""Search the owned documents for replaced values. Usage: python3 -I search_replaced.py
Prints every hit as FILE:LINE [FLAG] pattern-name | context. FLAG is HISTORY when the same line carries a marker word
(before, history, superseded, replaced, old, was, earlier, stale, CLOSED, no longer, v6, v7) else OPEN. Exit 0 always; the
review of each OPEN line is in text-pass-notes.md."""
import re, glob, os
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/")
FILES = [R+"architecture.md"] + sorted(glob.glob(R+"mfg/specs/*.md")) + [
 R+"mfg/assembly/assembly.md", R+"mfg/assembly/v7-update-notes.md", R+"mfg/parts-notes.md", R+"mfg/tools/draw.py",
 R+"mech/mic-path/mic-path.md", R+"mech/light-path/light-path.md", R+"mech/mech-notes.md", R+"mech/CHECKLIST.md",
 R+"mech/ring.py", R+"supplier-package/v3-notes.md"]
FILES = [f for f in FILES if not f.endswith("/cell.md")]
PAT = {
 "channel 6.8": r"6\.8 mm wide|6\.8 wide|channel 6\.8|6\.8 channel|6\.8 mm channel|6\.8 mm\)? channel",
 "edge wall 0.6": r"0\.6 mm at each edge|edge wall.{0,20}0\.6 mm",
 "slot 2.0 x 0.6": r"2\.0 x 0\.6|X -3\.5 to -1\.5|X -3\.5 to X -1\.5",
 "ribbon 1.4": r"1\.4 mm wide|1\.4 x 0\.15",
 "stiffener 0.075": r"0\.075 (mm )?stiffener|stiffener.{0,40}0\.075|x 0\.075",
 "6 layers": r"6 layers|6-layer|6 layer",
 "antenna notch": r"antenna notch|notch of the board, 1\.8|notch 1\.8|1\.8 x 3\.6",
 "Gore": r"Gore|GAW112",
 "skin-safe": r"skin-safe",
 "resin grade open": r"grade is open|resin grade",
 "two opposite switches": r"two opposite",
 "RC1 if adopted": r"only if the owner adopts|if adopted|if the owner adopts",
 "plane X -10.6": r"X -10\.6",
 "20.3 cubic": r"20\.3 cubic",
 "UV dam slots": r"UV-curing|UV cured|UV-cured",
 "tape not chosen": r"tape (itself )?is not chosen|tape not chosen|seal tape and its",
 "PSA": r"\bPSA\b",
 "stainless": r"stainless or polyimide|Stainless or polyimide",
 "TP22/DBG_RX": r"TP22|TP1 to TP22|DBG_RX",
 "S25 open": r"open item S25|Open item S25|S-L1",
 "PVD or DLC": r"PVD or DLC",
 "aluminosilicate": r"aluminosilicate",
 "membrane at most 0.10": r"at most 0\.10 thick|at most 0\.10 mm",
 "0.15 per side": r"0\.15 mm per side|0\.15 mm or less",
 "C84 X 1.2": r"C84.{0,40}X 1\.2,",
 "10 uF in and out": r"10 uF in and out",
 "antenna X -12.7": r"X -12\.7",
 "NOT DECIDED": r"NOT DECIDED",
 "Grepow answers": r"Grepow answers|Grepow\)",
 "mic port wall slots": r"in the block's wall away",
 "open point 5 pointer": r"open point 5",
 "S26 sealant open": r"sealant.{0,60}(open item S26|not chosen)",
}
HIST = re.compile(r"before|history|superseded|replaced|\bold\b|\bwas\b|earlier|stale|CLOSED|no longer|v6|v7|v8|17\.\d|inside model|\(\d{4}-\d\d-\d\d", re.I)
n_open = 0; n_hist = 0
for f in FILES:
    for i, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        for name, p in PAT.items():
            m = re.search(p, line)
            if m:
                flag = "HISTORY" if HIST.search(line) else "OPEN"
                if flag == "OPEN": n_open += 1
                else: n_hist += 1
                s = max(0, m.start()-70); e = min(len(line), m.end()+70)
                print(f"{f.replace(R,'design/')}:{i} [{flag}] {name} | {line[s:e].strip()}")
print(f"hits OPEN {n_open} HISTORY {n_hist}")
