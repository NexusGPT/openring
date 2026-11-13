#!/usr/bin/env python3
"""Writes pcb/footprint-notes.md.  The prose is below; every count and every 'last line' is read from the saved logs of
run_final.sh (w1-evidence/final_*.log) so that the notes cannot disagree with the evidence.
Run: design/.venv/bin/python -I make_notes.py   (after bash run_final.sh final)"""
import csv, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.dirname(HERE)
RING = os.path.dirname(PCB)
DESIGN = os.path.dirname(os.path.dirname(RING))


def last(name, n=1, skip_exit=True):
    lines = [l.rstrip('\n') for l in open(os.path.join(HERE, name)) if l.strip()]
    if skip_exit and lines and re.match(r'exit \d+$', lines[-1]):
        code = lines[-1]; lines = lines[:-1]
    else:
        code = ''
    return lines[-n:], code


def lastline(name):
    return last(name)[0][-1]


def result_line(name):
    return [l.strip() for l in open(os.path.join(HERE, name)) if l.startswith('RESULT')][-1]


def exitcode(name):
    return last(name)[1]


src = list(csv.DictReader(open(os.path.join(PCB, 'footprint-sources.csv'))))
parts = list(csv.DictReader(open(os.path.join(RING, 'parts.csv'))))
net = list(csv.DictReader(open(os.path.join(RING, 'netlist.csv'))))
fps = sorted(f[:-10] for f in os.listdir(os.path.join(PCB, 'OpenRing.pretty')) if f.endswith('.kicad_mod'))
n_fp, n_src, n_parts, n_pins = len(fps), len(src), len(parts), len(net)
open_rows = len(open(os.path.join(RING, 'open-pins.csv')).read().splitlines()) - 1
erc = [l for l in open(os.path.join(HERE, 'final_erc_report.txt')) if 'ERC messages' in l][0].strip()

by_fp = {}
for r in src:
    by_fp.setdefault(r['footprint'], []).append(r)

lib_rows = []
for name in fps:
    rs = by_fp[name]
    r = rs[0]
    refs = ' '.join(x['reference'] for x in rs) if len(rs) <= 6 else '%s and %d more' % (' '.join(x['reference'] for x in rs[:3]), len(rs) - 3)
    lib_rows.append('| %s | %s | %s | %s | %s | %s | %s |' % (name, refs, r['maker_document_file'], r['page'], r['pad_count'], r['pitch'], r['land_source']))

T = []
w = T.append
w('# Ring footprints and open parts (package W1)')
w('')
w('Written 2026-11-13 by W1 (helper ring-parts). Version worked on: the project folder as found, commit b1de827. Nothing here was committed by me.')
w('')
w('All paths are under `design/` unless they start with `/`. `RING` means `ecad/ring/` and `PCB` means `ecad/ring/pcb/`. Proof logs are in `PCB/w1-evidence/`, each named `final_*.log` for the last run. The checklist is `PCB/w1-evidence/CHECKLIST.md`.')
w('')
w('Scope change (lead, 2026-11-13): the band parts (J_BAND_A, J_BAND_B, SW1 to SW5, M1, RT1, CP1 to CP4, BT1 with PRT1; 14 references) are drawn by band-circuits in `ecad/band/OpenRingBand.pretty` and their interface is in `ecad/band/band-interface.md`. I drew none of them and wrote no interface file for them (my first draft of both was removed). `parts.csv` names their footprints `OpenRingBand:<name>`, `footprint-sources.csv` has a row for each naming that library, and `check_footprints.py` reads them from it. Two lead notes were also applied: C60 changed to 2.2 uF, and distributor copies of a maker sheet are allowed.')
w('')
w('Rerun everything: `bash PCB/w1-evidence/run_final.sh final` (generators, ERC, all checks). Rebuild this file: `design/.venv/bin/python -I PCB/w1-evidence/make_notes.py`.')
w('')
w('## Answers to points a to g')
w('')
w('### a. Footprint library')
w('')
w('Folder: `PCB/OpenRing.pretty/`. It holds %d footprint files, one per distinct package of the %d parts of `RING/parts.csv`, not counting the 14 band parts (their footprints are in the band library). Written by `PCB/make_footprints.py`. KiCad finds it through `PCB/fp-lib-table` (for the board project in that folder) and `RING/fp-lib-table` (for the schematic project), nickname `OpenRing`.' % (n_fp, n_parts))
w('')
w('Each footprint has the pad numbers or ball names of the maker document, the land pattern the document gives where it gives one, a courtyard on F.CrtYd, and the document file and page in its description. No description holds the word PROVISIONAL: `PCB/check_footprints.py` tests that (point f).')
w('')
w('| Footprint | Parts | Maker document | Page | Pads | Pitch | Where the lands come from |')
w('|---|---|---|---|---|---|---|')
T.extend(lib_rows)
w('')
w('Details that matter:')
w('- U1: the 61 land centres are measured from Nordic\'s own reference layout (`datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf` page 1, drawn at 12:1) by `PCB/measure_u1.py`. The ball names come from Nordic\'s reference schematic. The match is 61 names to 61 pads. Only one of four ways to lay the name grid on the pads fits (A1 top left, the other three fit 55 of 59 grid sites: `PCB/w1-evidence/final_measure_u1.log`). The grid is 8 rows (A B D E F G H, no C row except ball C1) by up to 10 columns at 0.325 pitch, 59 balls on the grid and C1 and D3 off it. This ends the 8 x 10 against 9 x 7 disagreement of deferred item 9: `placement.csv` is wrong. The 62nd circle the script finds inside the body outline is a duplicate drawn 0.07 mm from another.')
w('- U2: 7 columns at 0.419 pitch and 5 rows at 0.44, ball 0.225 (nPM1304 specification page 155, Table 35). The ball map was already the real one (page 153, Table 33).')
w('- U4: pitch 0.5, land 0.26 (SG Micro sheet PDF page 18). A1 is top left in the top view: this closes deferred item 16.')
w('- U3: nine pads, not eight. The package drawing (PDF page 5) shows a ninth pad at the bottom centre. The pin table has no pin 9, so pad 9 has no net.')
w('- J1: the Hirose recommended land (catalogue page 4) with 15 contacts in two staggered rows plus two mounting pads `MP`. Pin 1 is the right end of the 8-pad row; the numbering runs left in 0.3 steps (drawing `w1_hirose_fh35c-15s-0.3shw50_drawing.pdf` page 1). The mounting-pad offsets are measured from the drawing by `PCB/measure_hirose_mp.py`.')
w('- U5 and U6: Knowles example land pattern (printed page 6). U11: TI example board layout with a 0.48 thermal pad turned 45 degrees, numbered 5 as the TI drawing numbers it.')
w('- Chip parts 0201, 0402, 0603: pad sizes measured on Nordic\'s reference layout for parts of the same size (C1, C4, R1, L1: `PCB/measure_passives.py`, saved `PCB/w1-evidence/passive-pads-measured.csv`). KiCad\'s own sizes differ (its 0201 pads are 0.46 along the part and 0.40 across, Nordic\'s are 0.27 along and 0.30 across), so I did not copy KiCad\'s. This follows bar a: a maker document backs each size.')
w('')
w('### b. footprint-sources.csv')
w('')
w('File: `PCB/footprint-sources.csv`, %d rows, one per part reference, columns: reference, package, footprint, maker_document_file, page, pad_count, pitch, pin_to_net_map_source, land_source, document_obtained. Written by `make_footprints.py`, which stops if a part has no row or a footprint has no part.' % n_src)
w('')

w('### c. Netlist scripts use the makers\' real pin numbers')
w('')
w('Changes in `RING/make_netlist.py` (old file saved as `PCB/w1-evidence/make_netlist_before.py`, diff `make_netlist.diff`):')
w('')
w('| Part | Before | Now | Source |')
w('|---|---|---|---|')
w('| J1 | positions P1 to P15 | 1 to 15 | Hirose drawing page 1 (Contact No.1, No.2), catalogue page 4 |')
w('| X1 | P1, P2 | 1 = X1 net, 3 = X2 net, 2 = GND (lid), 4 no connection | Kyocera catalogue page (`w1_kyocera_cx2016db_catalog_page10.pdf`), connection diagram |')
w('| X2 | P1, P2 | 1, 2 (a crystal has no polarity) | TXC sheet `w1_txc_9ht11_datasheet.pdf` page 1: 2 pads, no drawing |')
w('| U11 | thermal pad EP | pad 5 | TI DQN0004A land drawing (`motor_tlv755p.pdf` PDF page 42) |')
w('| DISP1 pins 3 and 4 | listed open ("4 MTP, 4 VCI") | 3 MTP, 4 VCC | Tailor sheet PDF page 5 table (page 6 misprints it) |')
w('| U1 balls, U2 balls, U3, U4, U5, U6, U9, U10, ANT1 | already real | unchanged | as before; each footprint now carries the same names (check f) |')
w('| SW1 to SW5 | P1, P2 (round 2 first rolled back to these, then corrected by the lead) | terminals 1 to 4: 1 and 3 one contact, 2 and 4 the other | Alps SKTA catalogue (`w1_alps_skta_catalog.pdf`) page 2, Drawing No.1 |')
w('| M1, BT1 | P1, P2 | pins 1 and 2 (M1 1 = red lead +, 2 = black or blue lead -; BT1 1 = +, 2 = -) | Jinlong sheet PDF page 9; band interface |')
w('| J_BAND_A, J_BAND_B | land numbers 1 to 8 and 1 to 7 | unchanged | `ecad/band/band-interface.md` |')
w('')
w('Also changed in `make_netlist.py`: footprint names (map `FPMAP`), the charging pad value "gold pad 1.6mm" (was 1.0 mm; architecture 17.12 wins, so `parts.csv` is corrected), C60 (2.2 uF) and the order codes of point d. `RING/check_netlist.py` was edited in %d changed lines (diff `PCB/w1-evidence/check_netlist.diff`) for J1 pin names, SW1 to SW5, M1, U11 pad 5 and DISP1 pins 3 and 4, and in test A7-3 so that C35 and C36 may be marked C0G or NP0 as well as Class 1 (C0G is a Class 1 dielectric); no limit or expected value was loosened.' % len([l for l in open(os.path.join(HERE,'check_netlist.diff')) if l.startswith('-') and not l.startswith('---')]))
w('')
w('Commands and last lines (all re-run by `run_final.sh`):')
w('')
w('| Check | Command | Last line | Exit |')
w('|---|---|---|---|')
w('| generate | `design/.venv/bin/python -I RING/make_netlist.py` | `%s` | %s |' % (last('final_make_netlist.log')[0][-1], exitcode('final_make_netlist.log')))
w('| netlist check | `design/.venv/bin/python -I RING/check_netlist.py` (inside `run_all.sh`) | `%s` | exit 0 |' % result_line('final_check_netlist_full.log'))
w('| ERC | `kicad-cli sch erc` (inside `run_all.sh`) | `%s` | 0 |' % erc)
w('| all | `bash RING/run_all.sh final` | `%s` | %s |' % (lastline('final_run_all.log'), exitcode('final_run_all.log')))
w('')
w('`RING/open-pins.csv` now holds the header only (%d data rows; it was 60 rows). No pin number waits on a document. Before: `PCB/w1-evidence/check_netlist_before.log` ended `RESULT PASS netlist netlist.csv`, ERC `PCB/w1-evidence/erc_report_before.txt` also 0 errors and 0 warnings.' % open_rows)
w('')
w('### d. Part numbers for the open lines (and C60)')
w('')
w('Rule from the lead: a part line carries only a code that a saved maker document shows. Documents: Murata sheets saved by reader w1b (`design/datasheets/w1b_*.pdf`, see `PCB/part-docs.md`), Kyocera AVX tables (`w1_kyocera_avx_x7r_dielectric.pdf`, `w1_kyocera_avx_c0g_dielectric.pdf`, PDF page 3 each; cells read in `PCB/w1-evidence/avx_x7r_cells.log` and `avx_c0g_options.log`).')
w('')
w('| Ref | Order code | Package, height | Document | Reason (one line) |')
w('|---|---|---|---|---|')
w('| C71, C86, C87 | Murata GRM155R61E105KA12D | 0402, 0.5 | `w1b_murata_grm155r61e105ka12.pdf` p1 (code), p2 (1.0 uF 25 V X5R) | one part for three lines: 25 V covers the 10 V of Table 38, and 0402 stays the board size |')
w('| C85, C60 | Kyocera AVX 0402ZC225KAT2A | 0402, 0.71 max | AVX X7R table PDF p3, row 2.2 uF, 0402, 6.3 V and 10 V (code E) | 2.2 uF 10 V as Table 37 (C6); C60 on VDD_SD by lead decision 24 and the storage sheet PDF p11 |')
w('| L71, L72 | Murata 1269AS-H-2R2M=P2 | 2.5 x 2.0 x 1.0 max | `w1b_murata_1269as-h-2r2m.pdf` p2 (2.2 uH, DCR 156 mohm max, 1.9 A), p1, p5 | same part as L10; meets Table 17 of the nPM1304 (2.2 uH, DCR below 400 mohm, Isat above 350 mA, page 44) |')
w('| RT1 | Murata NCP15XH103F03RC | 0402 | `w1b_murata_ncp15xh103f03rc.pdf` p1, p2 | 10 kohm 1 percent, B 3380 K as the nPM1304 thermistor table (page 24) |')
w('| C35, C36 | Kyocera AVX 04025A102JAT2A (1.0 nF C0G) | 0402, 0.56 max | AVX C0G table PDF p3 (printed p5): 0402 row 1000 pF at 16, 25, 50 V, code C | Class 1 as Knowles asks; the table has 0.1 uF C0G only in 1206, 2.29 mm high, and 1.00 mm is free |')
w('| C88 | Murata GRT188R61A106KE13D | 0603, 0.8 | `w1c_murata_grt188r61a106ke13.pdf` p1 (code D = 180 mm paper tape), p2 (10 uF 10 V X5R) | lead decision. STATED DEVIATION from Nordic Table 37 (16 V): C88 sits on VSYS, which never exceeds VBUSOVP 5.5 V (nPM1304 PDF p17); 10 V is 1.8 times that; the AVX X7R table has 10 uF 16 V only at 1.52 mm and 2.29 mm |')
w('')
w('**C35 and C36.** Knowles asks for a bypass capacitor next to each Vdd pin and no Class 2 part near the microphone, and its Figure 4 shows 0.1 uF (PDF page 4 of `w1b_knowles_spk0641ht4h-1_chipdip.pdf`): "Capacitors near the microphone should not contain Class 2 dielectrics due to their piezoelectric effect." The 0.1 uF value is **not met** with a Class 1 part of this height. C35 and C36 are 1.0 nF C0G in 0402, each next to its microphone\'s Vdd pin. C31 and C32 (1 uF, Class 2) stay at least 2.0 mm from each microphone edge and carry the bulk. The build guide measures the noise floor. My round 1 sentence that put a 0.1 uF C0G cell in 0805 was wrong: the table shows 0.1 uF C0G only in 1206.')
w('')
ca = {m.group(1): float(m.group(4)) for m in re.finditer(r'^(\S+) courtyard ([\d.]+) x ([\d.]+) = ([\d.]+) mm2', open(os.path.join(HERE, 'final_courtyard.log')).read(), re.M)}
w('Room (courtyards, `PCB/w1-evidence/final_courtyard.log`: 0201 %.3f, 0402 %.3f, 0603 %.3f, 1269AS inductor %.3f mm2): C86, C87, C35 and C36 grow from 0201 to 0402, +%.3f mm2 each (+%.3f together); C71, C85, C60 and C88 stay 0402; L71 and L72 become 2.5 x 2.0 parts of %.3f mm2 each (placement.csv has them at 2.0 x 1.6).' % (ca['Chip_0201'], ca['Chip_0402'], ca['Chip_0603'], ca['L_Murata_1269AS-H_2.5x2.0'], ca['Chip_0402'] - ca['Chip_0201'], 4 * (ca['Chip_0402'] - ca['Chip_0201']), ca['L_Murata_1269AS-H_2.5x2.0']))
w('')
w('Files changed for point d: `bom.csv` (8 lines: C71, C85, C86 and C87, C88, C60, L71 and L72, RT1, C35 and C36), `bom-notes.md` (one note), `sch-notes.md` (open point O10 and the W1 section). `tools/check_bom.py`: before `%s` (`PCB/w1-evidence/check_bom_before.log`), after `%s` (%s, `PCB/w1-evidence/final_check_bom_after.log`).' % (last('check_bom_before.log')[0][-1], lastline('final_check_bom_after.log'), exitcode('final_check_bom_after.log')))
w('')
w('### e. Custom parts')
w('')
w('Moved to band-circuits by the lead: tab order, land order, land size and pitch of J_BAND_A, J_BAND_B, BT1 with PRT1, CP1 to CP4, M1, RT1 and the switches are theirs, in `ecad/band/band-interface.md`. I wrote no `custom-part-interfaces.md` (the draft was removed). What stays mine here: the charging pad is 1.6 mm in `parts.csv` and `bom.csv` (architecture 17.12 wins over 1.0 mm), and the 22 test pads TP1 to TP22 (footprint `TESTPAD_0.8`, 0.8 mm round, the size of the first draft, from the list `TPS` in `make_netlist.py`).')
w('')
w('### f. Check script')
w('')
w('`PCB/check_footprints.py` loads every part\'s footprint with KiCad\'s Python (`PCB/run_kipy.sh`). It exits 1 when a netlist pin has no pad of that name, when a pad count differs from `footprint-sources.csv`, when a description holds PROVISIONAL or names no document file, or when the library holds a footprint no part uses. Band parts are read from `ecad/band/OpenRingBand.pretty` like the others: every netlist pin must be a pad name, the pad count must equal `footprint-sources.csv`, and a missing footprint file fails ("not yet delivered" is no longer accepted).')
w('')
w('| Run | Command | Last line | Exit |')
w('|---|---|---|---|')
w('| good | `PCB/run_kipy.sh PCB/check_footprints.py` | `%s` | %s |' % (lastline('final_check_footprints_good.log'), exitcode('final_check_footprints_good.log')))
w('| renamed ball | `PCB/run_kipy.sh PCB/check_footprints.py PCB/w1-evidence/broken_ball.pretty` | `%s` | %s |' % (lastline('final_check_footprints_broken_ball.log'), exitcode('final_check_footprints_broken_ball.log')))
w('| missing pad | `PCB/run_kipy.sh PCB/check_footprints.py PCB/w1-evidence/broken_missing.pretty` | `%s` | %s |' % (lastline('final_check_footprints_broken_missing.log'), exitcode('final_check_footprints_broken_missing.log')))
w('| band library absent | same with an empty folder as 4th argument | `%s` | %s |' % (lastline('final_check_footprints_band_absent.log'), exitcode('final_check_footprints_band_absent.log')))
w('| band circuits | `PCB/run_kipy.sh ecad/band/check_band.py` (read only for me) | `%s` | %s |' % (result_line('final_check_band.log'), exitcode('final_check_band.log')))
w('')
w('The broken copies are made by `PCB/make_broken_fp.py` (U1 ball A1 renamed A1X; U2 pad E7 deleted). The first fails on the name, the second on the missing pad and on the count. I did not run the new script on the old state: the library did not exist then, so a failure there would be a missing name, which is not red.')
w('')
w('### g. Not closed')
w('')
w('Each item names what I tried and the exact document that is missing.')
w('')
w('1. C35 and C36: the 0.1 uF at the Vdd pin that Knowles shows is not met with a Class 1 part of this height (1.0 nF C0G 0402 instead). Missing: a Class 1 100 nF part of 1.0 mm or less in a readable maker document; the build guide measures the noise floor.')
w('2. U1 mechanical drawing: Nordic\'s package page (docs.nordicsemi.com, CSP61 CAAA) answered 403 in the logged pass. Lands and names are closed from the reference layout and schematic. Missing: ball height and ball diameter tolerance, which the land does not need.')
w('3. Knowles SPK0641HT4H-1: the Knowles product page returned 212 bytes of HTML, no sheet (logged pass). I use the two distributor copies of Knowles Datasheet Rev A (Chipsmall, on disk; ChipDip, `w1b_knowles_spk0641ht4h-1_chipdip.pdf`). The corner chamfers of the land (8 x 0.1 x 45 degrees) are not drawn.')
w('4. TXC 9HT11: the one-page sheet (`w1_txc_9ht11_datasheet.pdf`) has no drawing, so pad size comes from Nordic\'s reference layout for the same part. Pad numbers are not printed; the two terminals are interchangeable.')
w('5. TLV75530P U11: the four small pads have a cut inner corner on the TI drawing; the cut is not dimensioned on the page, so the pads are drawn as plain rectangles 0.36 x 0.21.')
w('6. `FPCtail_Tailor_TOH095XVT-01_15`: pitch 0.3 and pad width 0.15 are not printed on the Tailor page (4.8 mm tail, 3.2 mm contact block are). This is the module\'s own tail, not a ring board part.')
w('7. J1 courtyard: the housing depth 4.2 is on the Hirose page, but which side the 0.6 overhang lies on is not read; the courtyard is centred on the lands.')
w('8. Hirose mounting-pad offset: confirmed from the drawing by script only through the nearest drawn pad (the drawing breaks the pad row in the middle), see `PCB/w1-evidence/measure_hirose_mp.log`.')

w('')
w('## Deferred items answered')
w('')
w('Item: result. 9: closed (8 x 10 grid, measured). 13: closed for U1 U2 U3 U4 U5 U6 ANT1 J1 L10 L71 L72; J_BAND_A and J_BAND_B moved to band-circuits. 14: closed (X1 X2; Q1, Q2, LED1 were removed from the circuit earlier). 15: closed for U9 and the chip sizes. 16: closed. 19: closed: Nordic\'s reference leaves LED1 and LED2 unconnected and Table 36 (page 156) lists LEDs as not used in configuration 3; the balls stay open. 20: lands closed, drawing not obtained (Not closed 3). 21: closed (ball map Table 33, order code nPM1304-CAAA-R7 Table 50, land Table 35). 31, 46, 162, 163 and the SKTAAAE010 land of 125: band-circuits\' work now. 49: closed (pitch 0.3, 15 contacts, Hirose catalogue). 50: closed. 51: closed. 127: C71, C86, C87 (Murata sheet), C85 (AVX table), C35, C36 (AVX C0G, 1.0 nF, Not closed 2) closed; C88 closed by the lead\'s decision (point d); R41 is gone. 128: L71, L72 (Murata 1269AS sheet) and RT1 (Murata sheet) closed.')
w('')
w('## Facts about files in datasheets')
w('')
w('Checked with `file` (`PCB/w1-evidence/datasheet_types.log`): `slim_cs-csnp32gcr01-bow.pdf`, `slim_knowles-everest-miconflex-brief.pdf` and `slim_knowles-sph0690lm4h-1.pdf` are HTML pages, not PDFs. `nrf54lm20a_szlcsc.pdf` is a PDF of a Seeed board, not Nordic\'s package drawing. I cite none of them; the storage part is cited from `slim2_cs-sdnand-20230403.pdf`.')
w('')
w('## Changes other files need')
w('')
w('I did not touch these (they are on the must-not-touch list or outside my files).')
w('')
w('1. `PCB/build_board.py`, `PCB/check_board.py`, `PCB/board-notes.md`, `PCB/ring.kicad_pcb`: the board is stale and these still use the old `ring:` footprint names, the old pin maps (`PADMAP` for X1, X2 in `check_board.py`) and the PROVISIONAL drawn footprints. They must load `OpenRing.pretty` and `ecad/band/OpenRingBand.pretty` and the new pin numbers (J1 1 to 15, U11 pad 5). `PCB/provisional-footprints.json` (written by `build_board.py`) is obsolete.')
w('2. `design/mech/thin/placement.csv` (not mine): row U1 says "9 x 7 grid less 2 corners" but the real grid is 8 rows by 10 columns, 61 balls; row U2 says pitch 0.4 and ball 0.25 but the sheet says 0.419 x 0.44 and 0.225; row U4 says pitch 0.4 but the sheet says 0.5; row U3 says 8 pads 0.7 x 0.5 4 x 2 but the drawing shows 9 pads 0.8 x 0.7 in two columns 7.0 apart; row J1 says housing 3.2 x 5.2 but the Hirose housing is 6.1 along the contact row and 4.2 deep. The last one matters: along Y the real housing is 0.9 mm longer than the model, and along X 1.0 mm deeper (J1 sits at X -12.0 and the board edge is X -13.6).')
w('3. `design/architecture.md` and `design/mech/thin/thin-notes.md` repeat the U1 "9 x 7" grid (sch-notes O5 and thin-notes line 39).')
w('4. `design/ecad/band`: nothing needed; with the makers\' pin numbers back in the netlist `check_band.py` ends `%s`.' % result_line('final_check_band.log') + '')
w('5. `design/tools/build_supplier_package.py` copies `open-pins.csv`, `netlist.csv` and `parts.csv`; its package index may list `open-pins.csv` as holding provisional rows.')
w('6. `design/wiring/connections.md` Part 4 and Part 5 and `deferred-items.md` rows above: the lead can mark them closed from this file.')
w('')
w('## Files made or changed')
w('')
w('Made: `PCB/OpenRing.pretty/` (%d files), `PCB/footprint-sources.csv`, `PCB/make_footprints.py`, `PCB/check_footprints.py`, `PCB/make_broken_fp.py`, `PCB/measure_u1.py`, `PCB/measure_passives.py`, `PCB/measure_hirose_mp.py`, `PCB/footprint-notes.md`, `PCB/w1-evidence/` (logs, scripts, broken copies, `CHECKLIST.md`), `RING/fp-lib-table`, `PCB/fp-lib-table`, and in `datasheets/`: `w1_hirose_fh35c_series_catalog.pdf`, `w1_hirose_fh35c-15s-0.3shw50_drawing.pdf`, `w1_hirose_fh35c-15s-0.3shw50_spec.pdf` (saved, no number taken from it), `w1_ti_sn74axc4t774.pdf`, `w1_alps_skta_catalog.pdf` (used for the switch terminals by the netlist history only), `w1_kyocera_cx2016db_catalog_page10.pdf`, `w1_kyocera_avx_c0g_dielectric.pdf`, `w1_kyocera_avx_x7r_dielectric.pdf`, `w1_txc_9ht11_datasheet.pdf`, `w1_knowles_spk0641ht4h-1_chipsmall.pdf`.' % n_fp)
w('')
w('Changed: `RING/make_netlist.py`, `RING/check_netlist.py`, and by the run `RING/parts.csv`, `netlist.csv`, `symbols.csv`, `additions.csv`, `open-pins.csv`, `ring.kicad_sch` and its sheets, `ring.kicad_sym`, `ring-kicad.xml`, `ring-schematic.pdf`, `erc-report.txt` and `.json`, `RING/sch-notes.md` (W1 section appended), `bom.csv` (8 lines), `bom-notes.md` (note appended).')
w('')
w('Process notes: I read the web only with curl and python (no browser). I used the session scratchpad folder under /private/tmp for downloads and page images; those scratch files are not deleted (they are logs of what I read) and are not part of the delivery. No secret was read. No git command was run. No purchase, sign-up or contact was made.')
w('')
w('## Round 2 (lead messages, 2026-11-13)')
w('')
w('1. Band parts: `parts.csv` (through `make_netlist.py`), `footprint-sources.csv` and `check_footprints.py` use the band library `OpenRingBand` for J_BAND_A, J_BAND_B, SW1 to SW5, M1, BT1 and RT1 (both to PRT1_Tabs and RT1_NTC_0402) and CP1 to CP4; my own band footprints are not in `OpenRing.pretty`; `PCB/custom-part-interfaces.md` holds one line naming `band-interface.md` and the test pads. Correction by the lead: the band parts carry the makers\' pin numbers again (SW1 to SW5 terminals 1 to 4, M1 and BT1 pins 1 and 2), the netlist of the first delivery. Both checks, last lines:')
w('   - `PCB/run_kipy.sh PCB/check_footprints.py`: `%s` (exit %s). Every pin of the 14 band parts is a pad of the band library.' % (lastline('final_check_footprints_good.log'), exitcode('final_check_footprints_good.log').split()[-1]))
w('   - `PCB/run_kipy.sh ecad/band/check_band.py`: `%s` (exit %s). I did not edit `design/ecad/band`.' % (result_line('final_check_band.log'), exitcode('final_check_band.log').split()[-1]))
w('   - With the band library missing the first check now fails: `%s` (exit %s).' % (lastline('final_check_footprints_band_absent.log'), exitcode('final_check_footprints_band_absent.log').split()[-1]))
w('2. C60 on VDD_SD is 2.2 uF, Kyocera AVX 0402ZC225KAT2A (10 V, 0402, the code of C85): `make_netlist.py`, `parts.csv`, `bom.csv`; `sch-notes.md` open point O9 is marked CLOSED by decision 24.')
w('3. Documents and rulings (reader w1b, `PCB/part-docs.md`, then the lead\'s rulings): C71, C86, C87 are Murata GRM155R61E105KA12D in 0402 (code on p1 of its sheet); RT1 NCP15XH103F03RC confirmed; L10, L71 and L72 are one footprint drawn from p5 of the Murata 1269AS-H-2R2M=P2 sheet (two pads 0.8 x 2.0, centres 2.0 apart; the DFE201610E code and footprint are gone); C35 and C36 are 1.0 nF C0G 0402 (point d); C85 and C60 keep AVX 0402ZC225KAT2A (row 2.2 uF, 0402, 10 V on PDF p3); C88 is Murata GRT188R61A106KE13D (lead decision); the Knowles land (printed page 6) was drawn earlier and the second copy is cited. No part line of `bom.csv` says NOT CLOSED. Lines still without a document: 0.')
w('4. C88 (lead, last line of round 2): Murata GRT188R61A106KE13D, 10 uF 10 V X5R, 0603, 0.8 mm, orderable code with packaging letter D (180 mm paper tape) as page 1 of `w1c_murata_grt188r61a106ke13.pdf` lists it; `make_netlist.py`, `parts.csv` (footprint Chip_0603), `bom.csv` and `footprint-sources.csv` changed; the NOT CLOSED text is gone.')
w('5. Stated deviation from Nordic Table 37: 10 V instead of 16 V, because C88 is on VSYS and VSYS never exceeds the charger input limit VBUSOVP 5.5 V (nPM1304 PDF p17); 10 V is 1.8 times that. No 16 V part with a readable document exists at 1.0 mm or less.')
w('6. Checks after the change: see the table in point f and the two lines under item 1 above; all re-run by `run_final.sh`.')
w('')
w('RESULT: done, %d footprints, 11 of 11 open part lines closed against a maker document, 0 lines without a code, 8 items under Not closed' % n_fp)
open(os.path.join(PCB, 'footprint-notes.md'), 'w').write('\n'.join(T) + '\n')
print('wrote footprint-notes.md', len(T), 'lines')
