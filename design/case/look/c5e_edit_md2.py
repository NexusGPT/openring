"""C5e second pass: remaining Mill-Max figures in case-notes.md and case-architecture.md S4 (H03)."""
import os
CASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sub(fn, pairs):
    p = os.path.join(CASE, fn); t = open(p).read()
    for a, b in pairs:
        assert t.count(a) == 1, (fn, t.count(a), a[:60])
        t = t.replace(a, b)
    open(p, "w").write(t)
sub("case-notes.md", [
 ("The 4 pins push up with 4 x 90 gf = 360 gf; a printed snap latch carries it with no magnet sizing | DS p3_millmax_0981.pdf p.3 |",
  "The 4 Harwin pins push up with 4 x 0.39 N = 1.56 N (about 159 gf); a printed snap latch carries it with no magnet sizing (before C5e this row used the Mill-Max 0981's 4 x 90 gf = 360 gf; that pin does not fit) | DS p3_harwin_p70.txt (0.39 N +-0.09 N at 2.10 mm) |"),
 ("| Mill-Max 0900-8-15-20-76-14-11-0 or Harwin P70-6000045R instead of Mill-Max 0981 (read later by another helper, design/parts/ui-pass3.md lines 167 and 190) | 0900-8: mid stroke 0.495 mm leaves a +-0.25 mm window against +-0.35 mm for the 0981; P70: 0.39 N at 2.10 mm working height, 1 A. Kept as fallbacks if the 0981's 90 gf (4 pins = 360 gf) proves too high for the lid latch (bench B2); the 0981 has a full drawing read [DS] and is already proven in the model | design/parts/ui-pass3.md; DS p3_millmax_0981.pdf |",
  "| Mill-Max 0981 as the fitted pin (history, C2 to C5c) | Does not fit: flange 2.11 mm against the 1.60 mm pad pitch, and the pin holder bores are 1.60 mm for 1.50 mm barrels. The fitted pin since C5e is the Harwin P70-6000045R (0.39 N at 2.10 mm working height, 1 A; stroke not confirmed, K1). Mill-Max 0900-8-15-20-76-14-11-0 (mid stroke 0.495 mm) was a second option read by another helper and is not used | design/parts/ui-pass3.md lines 167 and 190; DS p3_millmax_0981.pdf |"),
 ("| O9 | Stack tolerance on pin compression: pin length ±0.15 mm [DS Mill-Max standard tolerance], board and print tolerances not measured; the window allows ±0.35 mm around 0.70 | bench |",
  "| O9 | Stack tolerance on pin compression: the Harwin P70's length tolerance and its stroke are not in the files read (not confirmed); board and print tolerances not measured; the contact window is 2.15 to 2.65 mm (my assumption) | bench |"),
 ("push the block down with more than 360 gf;", "push the block down with more than 159 gf (4 x 0.39 N, Harwin P70);"),
])
sub("case-architecture.md", [
 ("| Mill-Max, Harwin | a pin with barrel and flange at most 1.5 mm: stroke, force curve and life of the Harwin P70-6000045R (stroke is not in the catalogue page read); or Mill-Max confirmation that a 0981 layout at 1.6 mm exists |",
  "| Harwin | the stroke (at least 0.34 mm needed), force curve over 2.10 to 2.65 mm and life of the Harwin P70-6000045R (none is in the catalogue page read) |"),
])
print("ok")
