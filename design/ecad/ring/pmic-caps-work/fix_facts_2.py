p = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pmic-caps-facts.md")
s = open(p, encoding="utf-8").read()
pairs = [
 ("- CL03A104KP3NNNC: no Murata or other document on disk for this code. Voltage not stated.",
  "- CL03A104KP3NNNC is not a Murata part and no document for it is in the brief's list; voltage not stated in any document read."),
 ("- No capacitor is on the VDDIO ball alone; all share VDD_1V8. CL03A104KP3NNNC has no document on disk.",
  "- No capacitor is on the VDDIO ball alone; all share VDD_1V8. No document for CL03A104KP3NNNC was read."),
 ("- Voltage rating of the Kyocera/AVX 2.2 µF part 0402ZC225KAT2A (C85, C60): no document on disk covers it (`w13-kyocera-grep-all.log`: 0 hits). Not stated.",
  "- Voltage rating of the Kyocera/AVX 2.2 µF part 0402ZC225KAT2A (C85, C60): not in the two Kyocera files searched (`w13-kyocera-grep-all.log`: 0 hits); no other document searched. Not stated."),
 ("- Rating and DC bias of CL03A104KP3NNNC (100 nF, C1, C2, C5, C61, C72, C80, C81, C82): no document on disk. Not stated.",
  "- Rating and DC bias of CL03A104KP3NNNC (100 nF, C1, C2, C5, C61, C72, C80, C81, C82): no document read. Not stated."),
]
for a, b in pairs:
    print("found %d: %s" % (s.count(a), a[:50]))
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
