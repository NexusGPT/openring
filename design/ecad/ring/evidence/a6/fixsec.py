P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/evidence/a6/notes_a6_section.md")
s = open(P).read()
a = "the only supply names are VDD, DECD, DECA, DECRF, DECUSB, VBUS"
b = "the supply-type names are VDD, VSS, VBUS and the decoupling balls DECD, DECA, DECRF, DECUSB"
assert s.count(a) == 1; s = s.replace(a, b)
a = "a 1.8 V series exists only in the XTX document `datasheets/slim2_cs-csnp32gcr01-20260408.pdf`, which is another maker's family and not this part."
b = "the file `datasheets/slim2_cs-csnp32gcr01-20260408.pdf` holds the XTX XTSDx0xG datasheet (1.8 V and 3.3 V series, another maker's family), not the CSNP32GCR01-BOW."
assert s.count(a) == 1; s = s.replace(a, b)
open(P, 'w').write(s)
