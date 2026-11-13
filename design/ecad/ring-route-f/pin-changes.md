# Pin changes on ring-route-f (board pcb/ring.kicad_pcb, 2026-11-13 10:50)

The netlist check differs from this board exactly by these rows (`logs/check_board-final.log`, check 2, eight FAIL lines). Ball, port pin and position come from design/wiring/ring-board-plan.md (table a.3).
Used: 3 drops (rulings 1) and 2 moves (ruling 2). SPARE_P1_00, SPARE_P2_00, SPARE_P3_03 and SPARE_P3_04 are unchanged.

| Net | Old ball and port pin | New ball and port pin | Test pad affected |
|---|---|---|---|
| SPARE_P1_02 | U1 F8, P1.02 | dropped (F8 no net) | TP8 no net |
| SPARE_P1_14 | U1 F4, P1.14 | dropped (F4 no net, then used by LCD_TE) | TP9 no net |
| SPARE_P1_30 | U1 F9, P1.30 | dropped (F9 no net, then used by OLED_PWR_EN) | TP11 no net |
| LCD_TE | U1 D6, P1.22 | U1 F4, P1.14 (D6 no net) | none |
| OLED_PWR_EN | U1 E9, P1.29 | U1 F9, P1.30 (E9 no net) | none |

Why each was needed:
- SPARE_P1_02 dropped: LCD_MOSI (G8) gets out through F8's freed channel (step f21).
- SPARE_P1_14 dropped and LCD_TE moved D6 to F4: D6's escape channel freed for DECD at A6 (steps f22, f24); LCD_TE then routed from F4 (f25).
- SPARE_P1_30 dropped and OLED_PWR_EN moved E9 to F9: with only the drop, OLED_PWR_EN from E9 found no way to U4 C2 and its R66 leg cut a ground piece at R71 (steps f05 to f09); from F9 both legs close (f27 to f35).

Escapes changed (plan layers L1 = F.Cu, L2 = In1, L3 = In2, L4 = B.Cu), from `all-items-route-e-to-final.txt`:

| Ball | Net before -> after | Old escape | New escape |
|---|---|---|---|
| D6 | LCD_TE -> none | via L1-L3 in pad, L3 south to (3.997,-1.078) | none |
| E9 | OLED_PWR_EN -> none | via L1-L2 in pad, L2 east to (5.399,-0.002) | none |
| F4 | SPARE_P1_14 -> LCD_TE | via L1-L3 in pad, L3 south to (3.347,1.074) | via L1-L4 in pad |
| F8 | SPARE_P1_02 -> none | via L1-L3 in pad, L3 south to (4.650,1.074) | none |
| F9 | SPARE_P1_30 -> OLED_PWR_EN | via L1-L2 in pad, L2 east to (5.399,0.324) | via L1-L3 in pad |

Also removed (they belonged to nothing on one side): the MIC_A_DATA buried via L2-L3 at (2.000,0.324) and the NRESET buried via L2-L3 at (2.000,-0.002); MIC_A_DATA's L2 escape from F2 shortened from (2.000,0.324) to its last junction at (2.725,0.324). Both nets stay connected (`logs/drc-final.log`).
