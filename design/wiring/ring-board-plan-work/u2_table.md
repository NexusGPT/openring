| A1 | LED0 | (no connect) | 9.380, -1.257 | none | none | not connected: land only |
| A2 | LED1 | (no connect) | 9.380, -0.838 | none | none | not connected: land only |
| A3 | LED2 | (no connect) | 9.380, -0.419 | none | none | not connected: land only |
| A4 | LSOUT1/VOUTLDO1 | VDD_MIC | 9.380, +0.000 | L1 | none | L1 east (+X) to C86 |
| A5 | LSOUT2/VOUTLDO2 | VDD_SD | 9.380, +0.419 | L1 | none | L1 east (+X) to C87 |
| A6 | AVSS | GND | 9.380, +0.838 | L1 | none | L1 east (+X), 0.15 mm, into the L1 ground copper; its stacks to L4 sit at least 1.0 mm east of the body, off the B6 line of L2 (g.5) |
| A7 | PVSS1 | GND | 9.380, +1.257 | L1 | none | L1 east (+X), 0.2 mm, to its own GND stack L1-L4 at (10.00, 1.26) (PVSS1, NPM-DS schematic note) |
| B1 | VBUS | VBUS | 8.940, -1.257 | L1 | none | L1 north (-Y), 0.25 mm; joined to B2 by a 0.15 mm copper bridge on L1; then on L3 (0.60) to tail B pad 4 |
| B2 | VBUS | VBUS | 8.940, -0.838 | L1 | none | joined to B1 on L1 (same net) |
| B3 | CC2 | (no connect) | 8.940, -0.419 | none | none | not connected: land only |
| B4 | LSIN1/VINLDO1 | VDD_1V8 | 8.940, +0.000 | L2 | microvia L1-L2 in pad | L2 east (+X) through the A4 site |
| B5 | LSIN2/VINLDO2 | VDD_3V0 | 8.940, +0.419 | L2 | microvia L1-L2 in pad | L2 east (+X) through the A5 site |
| B6 | VOUT1 | VDD_1V8 | 8.940, +0.838 | L2 | microvia L1-L2 in pad | L2 east (+X) through the A6 site |
| B7 | SW1 | SW1 | 8.940, +1.257 | L1 | none | L1 south (+Y) to Y 1.65, east along Y 1.65 to X 10.20, south to the west pad of L71 (11.00, 3.45); 0.15 mm, no via |
| C1 | VSYS | VSYS | 8.500, -1.257 | L1 | none | L1 north (-Y), 0.15 mm, to C75, C76, C77; joined to C2 on L1 |
| C2 | VSYS | VSYS | 8.500, -0.838 | L1 | none | joined to C1 on L1 (same net) |
| C3 | VBUSOUT | VBUSOUT | 8.500, -0.419 | L2 | microvia L1-L2 in pad | L2 north (-Y) through the C2 and C1 sites, to C73 |
| C4 | GPIO3 | (no connect) | 8.500, +0.000 | none | none | not connected: land only |
| C5 | GPIO2 | (no connect) | 8.500, +0.419 | none | none | not connected: land only |
| C6 | VOUT2 | VDD_3V0 | 8.500, +0.838 | L2 | microvia L1-L2 in pad | L2 south (+Y) through the C7 site |
| C7 | PVDD | VSYS | 8.500, +1.257 | L1 | none | L1 south (+Y), 0.15 mm, to C74 at (8.50, 2.15), between the two switching tracks |
| D1 | VBAT | VBAT | 8.060, -1.257 | L1 | none | L1 north (-Y), 0.15 mm; joined to D2 on L1; then on L3 (0.30) to tail B pad 1 and C85 |
| D2 | VBAT | VBAT | 8.060, -0.838 | L1 | none | joined to D1 on L1 (same net) |
| D3 | NTC | NTC | 8.060, -0.419 | L2 | microvia L1-L2 in pad | L2 west (-X) through the E3 site |
| D4 | SHPHLD | SHPHLD | 8.060, +0.000 | L2 | microvia L1-L2 in pad | L2 west (-X) through the E4 site |
| D5 | CC1 | (no connect) | 8.060, +0.419 | none | none | not connected: land only |
| D6 | GPIO0 | PMIC_INT | 8.060, +0.838 | L2 | microvia L1-L2 in pad | L2 west (-X) through the E6 site |
| D7 | SW2 | SW2 | 8.060, +1.257 | L1 | none | L1 south-west to (7.60, 1.72), south along X 7.60 to the west pad of L72 (8.50, 3.45); 0.15 mm, no via |
| E1 | VSET2 | VSET2 | 7.620, -1.257 | L1 | none | L1 north (-Y) to R72 |
| E2 | VSET1 | VSET1 | 7.620, -0.838 | L1 | none | L1 west (-X) to R71 |
| E3 | SCL | PMIC_SCL | 7.620, -0.419 | L1 | none | L1 west (-X), toward U1 E7 |
| E4 | VDDIO | VDD_1V8 | 7.620, +0.000 | L1 | none | L1 west (-X) |
| E5 | SDA | PMIC_SDA | 7.620, +0.419 | L1 | none | L1 west (-X), toward U1 B8 |
| E6 | GPIO1 | (no connect) | 7.620, +0.838 | none | none | not connected: land only |
| E7 | PVSS2 | GND | 7.620, +1.257 | L1 | none | L1 west (-X), 0.2 mm, to its own GND stack L1-L4 at (7.00, 1.26) (PVSS2, NPM-DS schematic note), shared with the ground pad of C88 at (7.00, 1.95) |
