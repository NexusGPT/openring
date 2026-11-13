"""r4 edits, part 1: the lines of case-architecture.md and case-notes.md that the routed boards made wrong (board-notes.md Round 2 list items 5 and 6:
E1, R8, R9, R10, R21, LED1 anode). Each replacement must match exactly once; prints file, line number, old and new line."""
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EDITS = {
    "case-architecture.md": [
        ("--3V3--> U1, U4, LED1", "--3V3--> U1, U4 (LED1 anode: SYS)"),
        ("RGB LED1 (common anode on 3V3)", "RGB LED1 (common anode on SYS)"),
        ("| copper electrode 6 x 3 mm on the pin board, fifth wire W7 to U1 TOUCH4 (IO4) |",
         "| copper electrode on the pin board: front strip 3.9 x 1.15 mm plus a 4.1 x 4.6 mm back pour of the same net (18.9 mm2, design/ecad/case/pcb/board-notes.md conflict 7), fifth wire W7 to U1 TOUCH4 (IO4) |"),
        ("| U1 (355 mA peak), U4, LED1, pull-ups |", "| U1 (355 mA peak), U4, pull-ups (LED1's anode is on SYS: design/ecad/case/sch-notes.md section 9) |"),
        ("| to U2 CE (pin 9), 10 kΩ to GND (charging on by default) |",
         "| to U2 CE (pin 9), R21 10 kΩ to 3V3: charging off at power-on until the software has set the charger (design/ecad/case/sch-notes.md section 9) |"),
        ("| R8 470 Ω to LED1 red cathode (pin 2); active low |", "| R8 510 Ω to LED1 red cathode (pin 2), anode on SYS; active low |"),
        ("| R9 150 Ω to LED1 green cathode (pin 3); active low (bench B4) |", "| R9 270 Ω to LED1 green cathode (pin 3), anode on SYS; active low (bench B4) |"),
        ("| R10 150 Ω to LED1 blue cathode (pin 4); active low (bench B4) |", "| R10 270 Ω to LED1 blue cathode (pin 4), anode on SYS; active low (bench B4) |"),
    ],
    "case-notes.md": [
        ("| LED1 | common anode on 3V3, GPIO through R8-R10 to the cathodes, active low (architecture corrected; schematic already right) |",
         "| LED1 | common anode on SYS since the circuit simulation (design/ecad/case/sch-notes.md section 9; C2 had it on 3V3), GPIO through R8 510, R9 270, R10 270 ohm to the cathodes, active low |"),
    ],
}
for fn, reps in EDITS.items():
    p = os.path.join(D, fn)
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        n = s.count(a)
        assert n == 1, (fn, a, n)
        i = s.index(a)
        ln = s[:i].count("\n") + 1
        line_old = s.split("\n")[ln - 1]
        s = s.replace(a, b)
        print("%s:%d\n  - %s\n  + %s" % (fn, ln, line_old, s.split("\n")[ln - 1]))
    open(p, "w", encoding="utf-8").write(s)
print("done")
