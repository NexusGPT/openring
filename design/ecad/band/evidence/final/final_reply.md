W4 done: 14 flat flexible circuits drawn, routed, checked, with fab files.

Where: design/ecad/band/ (notes: band-notes.md, interface: band-interface.md). No git, no branch, nothing outside the folder except 2 maker documents design/datasheets/w4_alps_skta_catalog.pdf and w4_alps_sktaaae010_spec.pdf.

Checks (final runs in evidence/final/):
- check_band.py: exit 0, last line `RESULT: PASS boards checked 14`. 14 of 14 boards show kicad-cli drc 0 violations, 0 unconnected. Connectivity is computed from the copper shapes and matches netlist.csv.
- Broken copies (swapped line, missing land, wrong length): each exit 1.
- Outline length equals the model path plus the fold and foot (2.071 mm) at every size, against both the thin.py formulas and the STEP files (diff 0.0000 to 0.0001). FLEX1 16.115 (US 7) to 18.058 (US 13); FLEX2 32.184 to 39.485.
- Library OpenRingBand.pretty: 10 footprints, each with document and page. Alps terminals 1 to 4 as in the Alps drawing.
- fab/: Gerber, drill and a PDF drawing for each of the 14 boards, 7.9 MB for the folder.

Decisions: stack 25 um PI, 12 um copper, 0.11 mm finished, PI stiffener 0.10 (JLCPCB flex capability page). Board lands: 2 rows x 4, 0.30 x 0.55, hot bar. Fold inner radius 0.70 against minimum 0.66. Motor and cell lines 0.20 wide; longest drop 12.9 mV (motor, 175 mA) and 12.5 mV (cell, 227.5 mA). PRT1 joins VBAT, NTC, GND on lands 1, 3, 2; RT1 ground is on land 2 (CELL-). Switch ground runs through a B.Cu star in the head to lands 6 and 8.

Changes other files need (full table in band-notes.md): thin.py tail_w 1.4 to 1.8 and tail_x -2.6 to -2.5 (1.4 cannot hold the lines), stiff_t 0.075 to 0.10, FLEX2 strip X -2.25 to -3.4; parts.csv CP1 to CP4 1.0 to 1.6 mm and the J_BAND and band-part footprints; J_BAND on the ring board at X -2.25, Y +-4.325.

Not closed: fit of the 1.8 neck in the 3D model (I may not run it), hot bar and iron values are starting values until a built unit is measured, PRT1 tab interface is my requirement to the cell supplier, via-in-pad acceptance.

Last line of band-notes.md: RESULT: done, 14 boards (flex1-us7 to us13, flex2-us7 to us13), each kicad-cli drc 0 violations and 0 unconnected, check_band.py exit 0 on all 14 and exit 1 on 3 broken copies
