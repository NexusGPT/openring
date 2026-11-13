p = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pmic-caps-facts.md")
s = open(p, encoding="utf-8").read()
pairs = [
 ("| Mode difference | Not applicable. Config 1 has three 10 µF here, config 2 has three, config 3 has one. | - |",
  "| Mode difference | Config 1 lists C2, C3, C4 here; config 2 lists C2, C4; config 3 lists C4 (BOM rows above). | - |"),
 ("- Pin side: each capacitor's pin 2 is on GND (netlist lines 65 to 77 and 67 for C88 is not on GND; see netlist.csv for the pin 2 rows).",
  "- Pin 2 of C74, C75, C76, C77 and C88 is on GND (netlist lines 71, 72, 73, 74, 85)."),
 ("- L71 on VDD_1V8 (pin 2, netlist line 316), 3.768 mm... see netlist; L71 is 5.143 mm and L72 3.768 mm from U2 (placement-final.csv).",
  "- Coil placement from U2 centre (placement-final.csv): L71 5.143 mm, L72 3.768 mm. Coil pin 2 is on VDD_1V8 (netlist line 316) and VDD_3V0 (line 332)."),
 ("Picture: C7 and C8 on VOUT1 and VOUT2 at the far end of the coil, Figure 57.",
  "Picture: C7 on VOUT1 and C8 on VOUT2, Figure 57."),
 ("Table 20 | \"Soft start current limit = 25 mA, 10 µF, 0 V\" (4728)",
  "Table 20 | \"Soft start current limit = 25 mA, 10 µF, 0 V\" (4728)"),
 ("the 1.0 µF, 2.2 µF and 10 µF capacitors are 0603", "the 1.0 µF, 2.2 µF and 10 µF capacitors are 0603"),
]
for a, b in pairs:
    n = s.count(a)
    print("found %d: %s" % (n, a[:60]))
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
