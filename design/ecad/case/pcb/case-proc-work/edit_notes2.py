F=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/case-proc-notes.md")
t=open(F,encoding="utf-8").read().rstrip("\n").split("\n")
assert t[-1].startswith("RESULT:")
t.pop()
while t[-1]=="": t.pop()
sec="""
## Second item: first power-up test of the case main board (16:00 to 16:06 CET, clock from `date`)

Change. File: P/board-notes.md, step 1, new last sub-step "(g) First power-up test of the case main board, before any wire is soldered": the end of the step 1 line names it, and 22 indented lines follow it (g1 the connection, g2 the order, then one line per rail and per test pad, then the four hidden joint groups H1 to H4, then one line of what the test does NOT prove). Step 1 (e) now points to (g) instead of "open, for the lead". Later step numbers are unchanged (2 to 10). Script: W/edit_pu.py, W/edit_pu2.py, W/edit_pu3.py (logs edit_pu*.log). Text files read for it: W/txt/ (pdftotext copies of case_bq25895.pdf, case_esp32s3_mini1.pdf and case_esp32s3_ds.pdf; every page cited was computed from them).

What the test gives (all values from the cited files):
- Connected: bench supply 5.0 V, limit 1.5 A, on J1 VBUS and GND only; no cell, no pin board, no wire (sources in line g1).
- Lines with an expected value: VBUS_IN above 3.6 V (BQ p.7); SYS 3.50 to 3.65 V no load, up to 4.42 V loaded (BQ p.7); REGN 4.7 V or more (BQ p.10); 3V3 3.274 to 3.341 V (SN line 74, SL lines 126 and 127); VRING off, under 0.1 V (SL R2.5 as a stand-in limit); LED hand test across R8 1.53 to 2.35 V, across R9 and R10 0.59 to 1.27 V (CS lines 114 to 119, [CALC] mA times ohm); CHG_STAT and CHG_CE_N high; TP1 and TP2 high (the 3V3 reading); TP3 activity after power-up.
- Serial pad: ES p.15 says the ROM prints to UART0 by default; the message text, baud rate and timing are in no saved document (W/search_boot.log), so only "activity" is written.

Left for the lead (no expected value in the files, written as such in the lines):
- TP4 RXD0; TP6 to TP15 (SPARE_IO33 to IO42): no expected value; unpowered short check only (below about 50 ohm, the step 9 limit).
- TP5 QON: only a typical 4.3 V (BQ p.10), no range.
- Resistance in ohm of VBUS_IN, SYS, 3V3 to GND (unpowered), and the idle supply current in mA.
- The three LED line voltages with the module pins undriven (CS section 9 gives only a bound near 3.7 V).
- The VRING "off" limit of 0.1 V is borrowed from a ring row; no file gives one for VRING.
- BAT pad (W5) with no cell; the charger's STAT or fault display with TH1 not fitted.
- No test for the charger's centre pad (H4): an X-ray or a section.
- The simulation rows C4.1 to C4.4 (SL lines 122 to 125) still name 470 and 150 ohm and a 3V3 supply; they predate sim finding 3 and were not used.

Not proven by the test (also written in step 1 (g)): solder under the charger's centre pad; every module signal joint except TXD0; a single missing module ground joint; the charger's BAT pins; charging; VRING current limit and boost; the module's LED drive; TH1; the SD NAND; USB data.

Checks after the change (same commands as before; logs in W):
- check_boards.py (CHECK_BOARDS_TMP = W/cb_tmp): last line `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0 (W/check_boards_after2.log).
- check_case_docs.py: last line `RESULT PASS (0 findings)`, exit 0 (W/check_case_docs_after2.log).
- check_wiring.py --require-complete: exit 0, last line `RESULT PASS lines 68 (67 conductors, 1 sensing gap), drawn and routed 26, specified and landed 41, drawn, not routed 0, stated in text only 1, not drawn 0, complete 67 of 67 conductors (100 percent), problems 0` (W/check_wiring_after2.log). It is 67 of 67 and not 66 of 66 because another helper added one conductor to the ring files before this run; the case rows are unchanged.
- Lines moved: the two lines the wiring generator cites ("Which end first", "Order inside each end") moved from 296 and 298 to 318 and 320. build_wiring.py was run again (W/build_after2.log): against the list before this run (W/wbefore2/product-wiring.csv) 5 rows differ, the 5 case wire rows (W064 to W068 in the new numbering), and only in their cited board-notes line numbers. Both cited lines now read 318 and 320 in the five rows. system-joints.csv: not changed; draw_wiring.py not run (no label changed).
- Copper: not touched in this item (no board file was opened for writing).
- Not done: the automatic claim audit of rule 4 beyond these checks; nothing was built on a real board.

questions_for_owner: none
"""
t += sec.split("\n")
t += ["", "RESULT: done, step 1 (g) first power-up test written with 22 lines (connection, order, rails, 16 pads, 4 hidden joint groups, what is not proven), later step numbers unchanged, check_boards and check_case_docs pass, check_wiring --require-complete exit 0 (67 of 67)."]
open(F,"w",encoding="utf-8").write("\n".join(t)+"\n")
print("ok")
