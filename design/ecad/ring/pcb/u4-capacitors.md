# U4 (SGM38046) capacitors C21, C24, C25, C26, C27: 0402 parts

Written 2026-11-13 by ring-parts. Read only on the circuit files. All paths are under `design/`. Page numbers are PDF pages. Sheet: `datasheets/p3_sgm38046.pdf` (SG Micro, April 2022, 20 pages).

## 1. What the SGM38046 sheet says

Mapping of the ring's parts to the sheet's Figure 1 (page 4): C21 is the sheet's C1 (PVIN), C24 is C4 (VOUT), C25 is C5 (OVDD), C26 is C6 (AVDD), C27 is C7 (VON).

Sheet text on capacitors (whole sheet searched for "capacit"): page 3 "Place a bypass capacitor between this pin and ground" (AVIN only); page 15, layout: "The input and output bypass capacitors should be connected to the PCB ground plane" and place components close to the device. Table 1 (page 4) lists 4.7 uF / 16 V / X5R GRM188R61C475KAAJD (0603) for C1, C6, C7 and 10 uF / 16 V / X5R GRM188R61C106KAALD (0603) for C4, C5. Table 2 (page 4, "compact space and light loadings, below 50 mA") keeps the same 4.7 uF and 10 uF 16 V 0603 parts.

The sheet gives **no** minimum effective capacitance, **no** sentence on DC bias, and **no** smaller value for these five positions (Table 2 changes only L1 and C3). It lists 16 V parts, but states no rule for the rating.

| Ring part | Sheet position | Net | Highest voltage of the net, with page | Sheet value |
|---|---|---|---|---|
| C21 | C1 | VBAT = PVIN | 4.35 V: the ring's cell charge voltage (`mfg/specs/cell.md`, charge voltage 4.35 V). The sheet allows 2.7 to 5.5 V on PVIN (page 2, recommended operating conditions; page 5, input supply range), absolute maximum 6 V (page 2); over-voltage protection above 5.7 V (page 14) | 4.7 uF |
| C24 | C4 | SGM_VOUT | 4.9 V: buck-boost output voltage range 3.6 to 4.9 V (page 5, VOUT_RANGE); VOUT = MAX(VAVDD, VOVDD, abs(VOVSS)) + 0.3 V (page 14) | 10 uF |
| C25 | C5 | ELVDD (OVDD) | 4.6 V: OVDD range 2.8 to 4.6 V (page 6, VOVDD_RANGE) | 10 uF |
| C26 | C6 | SGM_AVDD | 3.3 V: AVDD fixed 3.3 V (page 5, VAVDD_RANGE) | 4.7 uF |
| C27 | C7 | SGM_VON | 4.1 V in magnitude, negative: VON range -4.1 to -0.7 V (page 5, VON_RANGE); absolute maximum -6 to 0.3 V (page 2) | 4.7 uF |

## 2. 0402 parts with a saved document

Three 0402 codes have a saved maker document. The Murata sheet named in the request, `datasheets/motor_murata_GRM155R60J475ME47.pdf`, is an HTML page, not a sheet, so it is not used. No document for the Murata 10 uF 6.3 V code was on disk; I fetched one.

| Code | Value, rating, dielectric | Size, thickness | Document and pages | Bias data |
|---|---|---|---|---|
| Murata GRM155R61A475MEAAD (code D = 180 mm paper tape) | 4.7 uF +-20 %, 10 Vdc, X5R | 1005M (0402), T 0.5 +-0.15 mm (0.65 max) | `datasheets/w1d_murata_grm155r61a475meaa.pdf` p1 (specification, packaging codes), p2 (graphs). Copy of https://akizukidenshi.com/goodsaffix/GRM155R61A475MEAA.pdf (Murata-printed Japanese sheet) | p2 "DC bias" graph, read from the image `pcb/w1-evidence/pages/w1d_murata_grm155r61a475meaa-2.png`: about 4.65 uF at 0 V, 3.9 at 2 V, 2.6 at 4 V, 1.8 at 6 V, 0.9 at 10 V |
| Murata GRM155R60J106ME15D | 10 uF +-20 %, 6.3 Vdc, X5R | 1005M (0402), T 0.5 +-0.15 mm (0.65 max) | `datasheets/w1d_murata_grm155r60j106me15.pdf` p1, p2. Copy of https://akizukidenshi.com/goodsaffix/GRM155R60J106ME15.pdf | p2 graph (`pages/w1d_murata_grm155r60j106me15-2.png`): about 10.1 uF at 0 V, 5.8 at 2 V, 4.0 at 3 V, 3.0 at 4 V, 2.4 at 5 V, 1.65 at 6.3 V |
| Kyocera AVX 0402ZC225KAT2A | 2.2 uF, 10 V, X7R | 0402, T 0.71 max (code E) | `datasheets/w1_kyocera_avx_x7r_dielectric.pdf` PDF p3 | no bias data in the document |

The AVX X7R table (same page) has no 4.7 uF cell and no 10 uF cell in 0402: its 4.7 uF starts in 0603 at 6.3 V, its 10 uF in 0805. So AVX does not help here. Curve values are read from graphs by eye and are good to about 0.1 uF.

## 3. Verdict per capacitor

Rule of the request: rated voltage at least 1.3 times the highest voltage of the net, and a document-backed code.

| Part | Candidate | Highest voltage | Rated / highest | Effective capacitance at that voltage (curve) | Verdict |
|---|---|---|---|---|---|
| C21 (4.7 uF, VBAT) | GRM155R61A475MEAAD | 4.35 V (sheet range 5.5 V) | 2.30 (1.82 at 5.5 V) | about 2.4 uF at 4.35 V, 51 percent (about 2.0 uF at 5.5 V) | **0402 possible with a smaller effective value** (about 2.4 uF) |
| C24 (10 uF, SGM_VOUT) | GRM155R60J106ME15D | 4.9 V | 1.29 | about 2.5 uF at 4.9 V, 25 percent | **stays 0603**: 1.29 is below 1.3, and a quarter of the value is left; no 10 V or higher 10 uF 0402 with a document was found |
| C25 (10 uF, ELVDD) | GRM155R60J106ME15D | 4.6 V | 1.37 | about 2.7 uF at 4.6 V, 27 percent | **0402 possible with a smaller effective value** (about 2.7 uF of 10) |
| C26 (4.7 uF, SGM_AVDD) | GRM155R61A475MEAAD | 3.3 V | 3.03 | about 3.05 uF at 3.3 V, 65 percent | **0402 possible with a smaller effective value** (about 3.05 uF) |
| C27 (4.7 uF, SGM_VON) | GRM155R61A475MEAAD | 4.1 V in magnitude | 2.44 | about 2.55 uF at 4.1 V, 54 percent | **0402 possible with a smaller effective value** (about 2.55 uF) |

Notes for the lead:
- The 0603 parts of the sheet's table (16 V) lose capacitance under bias too; the sheet gives no data for them and no minimum for any position, so I cannot say whether the 2.4 to 3.05 uF left on the 4.7 uF positions, or the 2.7 uF on C25, is enough. The sheet does not forbid it; the bench has to show the ripple.
- C25 has the lowest ratio of the three accepted 10 uF cases (1.37) and keeps the smallest share (27 percent). If the panel runs at the top of its ELVDD window, 4.6 V is the sheet's maximum, so the ratio does not fall below 1.37.
- If C24 must be 0402 anyway, a 10 uF 0402 code rated 10 V or more is needed; none has a document on disk or came back from the one distributor host I could read (guessed Murata names for 10 V and 16 V 10 uF 0402 returned 404). That is the missing document.
- Thickness: all three 0402 codes are 0.65 mm or less (Murata 0.5 +-0.15; AVX 0.71 max), inside the 0.8 mm limit.

RESULT: done, 4 of the 5 capacitors (C21, C25, C26, C27) can be 0402 with a smaller effective value, and C24 stays 0603 because 6.3 V is only 1.29 times its 4.9 V
