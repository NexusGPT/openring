# nPM1304: Nordic's reference circuit against the ring's wiring A6

Source: Nordic "nPM1304 Product Specification" v1.0 (`design/datasheets/npm1304_datasheet_v1_0.pdf`, from the owner, 2026-11-11). Figure 57 "CSP schematic" and Table 37 "Bill of material", page 157; Table 36 "PCB application configuration", page 156; "Output voltage selection", page 43. The figure was read from a picture of the page: `design/ecad/ring/evidence/npm1304/p157-csp-schematic.png`. Ball numbers: `npm1304-balls.csv` (Table 33, page 153).

Read by the lead. Nothing in the wiring files is changed here: the changes below go into the next wiring revision.

## What agrees

| Item | Nordic (page 156, 157) | Ring, wiring A6 and parts list | Result |
|---|---|---|---|
| Buck 1 voltage | VSET1 resistor 47 kohm gives 1.8 V | R71 47 kohm | same |
| Buck 2 voltage | VSET2 resistor 150 kohm gives 3.0 V | R72 150 kohm | same |
| Resistor tolerance | 5 % or better (page 43, page 157) | 1 % | better |
| Buck coils | L1, L2 2.2 uH, resistance under 400 milliohm, 0806 | L71, L72 2.2 uH, 0806, no part number yet | same value; the part must meet the 400 milliohm limit |
| VBUSOUT capacitor | C5 1.0 uF, 10 V | C73 1.0 uF | same value |
| VDDIO capacitor | C13 100 nF | C80 100 nF | same |
| Buck output capacitors | C7 10 uF on VOUT1, C8 10 uF on VOUT2 | C78 10 uF on VDD_1V8, C79 10 uF on VDD_3V0 | same value |

## What differs (to correct at the next wiring revision)

| No | Item | Nordic | Ring today | What to do |
|---|---|---|---|---|
| D1 | VBUS capacitor | C1 1.0 uF, X5R, **25 V** | C71 4.7 uF, part GRM155R60J475ME47D, which is a **6.3 V** part (the "0J" in its code), plus C72 100 nF | Replace C71 by a 1.0 uF capacitor rated 25 V. The chip accepts 22 V transients on VBUS (product brief): a 6.3 V capacitor on a 5 V line that people plug in is under-rated. |
| D2 | VBAT capacitor | C6 2.2 uF, 10 V, at the VBAT balls | C21 on the net VBAT (4.7 uF) | Check C21's value and place against 2.2 uF at balls D1, D2; add one if C21 serves another part. |
| D3 | VSYS and PVDD capacitors | C2, C3, C4: three of 10 uF, 16 V, at balls C1, C2 and C7; two of them return to PVSS1 and PVSS2 | C74, C75 10 uF and C76, C77 1.0 nF on VSYS | Add a third 10 uF; return them to PVSS1 and PVSS2 as drawn; the 1.0 nF pair came from the older chip's kit and is not in this reference. |
| D4 | Load switch or regulator outputs | C9 to C12: two of 10 uF on each output, for the regulator mode of configuration 1 | VDD_MIC and VDD_SD are used as switches with small capacitors | Read the specification's LOADSW chapter for the capacitor rule in switch mode before the revision; not read here. |
| D5 | GPIO4 | not on the small package | drawn as an unused pin | Remove. |
| D6 | Ground of the two bucks | PVSS1 (A7) and PVSS2 (E7) each joined to the ground layer by its own via ("net tie") | all on GND | Keep as a layout rule for the board. |
| D7 | Capacitor size | Nordic lists 0603 for every capacitor | the ring uses 0402 and 0201 | A 10 uF 0402 loses much of its value under voltage; the electronics designer must check the real value at 3.0 V and 4.35 V. |

State on 2026-11-13: D1 is done (C71 is 1.0 uF, 25 V). D2 to D7 are decided in `design/wiring/lead-decisions.md`, row "power chip capacitors against Nordic's datasheet", from the facts of `design/ecad/ring/pmic-caps-facts.md`: one change (a second 10 uF, C90, on the 3.0 V rail) and one board check (own ground vias for balls A7 and E7). Row D3's "add a third 10 uF" was already met by C88; row D7's "0603 for every capacitor" is not what the maker's tables say (C13 is 0201).

RESULT: read, 7 agreements, 7 differences listed for the wiring revision, nothing changed in the wiring files.
