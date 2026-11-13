"""Searches the Nordic documents on disk for input-level limits (VIH, VIL, input high, input low) of the nRF54LM20A.
Usage: python search_nordic_limits.py > results/search_nordic_limits.log   Every file searched is listed with its hit count."""
import glob, os, re, warnings
warnings.filterwarnings("ignore")
import fitz
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/datasheets/")
files = sorted(set(glob.glob(D + "nrf54lm20*") + glob.glob(D + "mcu_*") + glob.glob(D + "antenna_nordic*") + glob.glob(D + "bench_nrf*") + glob.glob(D + "nordic-web/*") + glob.glob(D + "bench_npm*") + glob.glob(D + "p3_npm1300_ek_ug110.pdf")))
pat = re.compile(r"\bV\s?IH\b|\bV\s?IL\b|input high|input low|high-level input|low-level input|logic level", re.I)
for f in files:
    name = os.path.basename(f)
    try:
        if f.endswith(".pdf"):
            doc = fitz.open(f)
            text = "\n".join(p.get_text() for p in doc)
            pages = len(doc)
        else:
            text = open(f, errors="replace").read()
            pages = 0
    except Exception as e:
        print("%-50s cannot read: %s" % (name, str(e)[:60]))
        continue
    hits = [m.group(0) for m in pat.finditer(text)]
    print("%-50s %3d pages, %6d chars, %2d hits %s" % (name, pages, len(text), len(hits), sorted(set(h.lower() for h in hits))[:4]))
