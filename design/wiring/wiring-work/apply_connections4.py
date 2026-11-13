F = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/connections.md")
CSV = "design/wiring/product-wiring.csv"
CELLS = {
 "R8": "Inside the purchased cell pack (13 Nov, lead's ruling 08:31: BT1 + PRT1 + RT1 is one part): RT1 pin 2 joined to tab P- on the PRT1 board (band-interface.md line 114). %s: 1 line `specified and landed`, carrier kind `inside the part`." % CSV,
 "R10": "Specified and landed (13 Nov): the pack's three output tabs P+ (BT1 pin 1, VBAT), P- (BT1 pin 2, GND), NTC (RT1 pin 1) on FLEX2 lands PRT1_Tabs 1, 2, 3, which hold those nets in the 7 FLEX2 boards; nickel strip 0.30 x 0.10, hand soldered (band-interface.md section 5). %s: 3 `tab` lines `specified and landed`." % CSV,
 "R15": "Each end is drawn in its own files (CP1 to CP4 in the FLEX2 boards; P1 to P4 in case_pins.kicad_pcb); the pairing is text only until design/wiring/ring-case-contact.csv exists (lead's ruling 08:31: pairing by coordinates at 7 sizes, every in_range yes, maker range in design/case/pin-travel.md). %s: 4 lines `stated in text only` at the build of 08:33." % CSV,
}
OLD = "those 9 lines are now `specified and landed`.\n\n"
ADD = ("Update 2026-11-13 08:34 CET (product-wiring helper, fourth pass): cells R8, R10 and R15 follow the lead's rulings of "
       "08:31 (cell pack as one purchased part; pad-to-pin lines closed by design/wiring/ring-case-contact.csv).\n\n")
text = open(F, encoding="utf-8").read()
assert "fourth pass" not in text and text.count(OLD) == 1
lines = text.split("\n"); part1 = False; changed = 0
for i, ln in enumerate(lines):
    if ln.startswith("## Part 1."): part1 = True
    elif ln.startswith("## Part 2."): part1 = False
    if part1 and ln.startswith("| "):
        jid = ln.split(" | ")[0][2:].strip()
        if jid in CELLS:
            body = ln[:-2]; k = body.rfind(" | "); lines[i] = body[:k] + " | " + CELLS[jid] + " |"; changed += 1
open(F, "w", encoding="utf-8").write("\n".join(lines).replace(OLD, OLD + ADD)); print("cells changed:", changed)
