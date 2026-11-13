D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/assembly/assembly.md"
LD="lead-decisions.md row "
M9="model-v9-notes.md section m"
RC=LD+"'resin radio corner RC1, how it is made' 2026-11-13 04:28; radio corner default 2026-11-13 00:39"
EDITS=[
# line 11
(F,"- CHANNEL: the open groove inside the band, 6.8 mm wide, open toward the finger","- CHANNEL: the open groove inside the band, 7.0 mm wide (6.8 before inside model v8), open toward the finger",M9+" row assembly.md lines 11, 250; "+LD+"'band edge wall' 2026-11-13 03:24"),
# line 23 state of files
(F,"State of the files today (2026-11-12). The inside model v7 (no light parts, round joystick) is measured:","State of the files today (2026-11-13: the inside model is v9, `design/mech/thin/model-v9-notes.md`; the fit check of v9 ends `RESULT PASS` at US 7 to 13 with 48 parts on US 7, 8 and 9 and 47 on US 10 to 13; the maker files are written from v9, `design/mfg/parts/index.csv`, 104 files). History, state of 2026-11-12: the inside model v7 (no light parts, round joystick) is measured:","model v9 (model-v9-notes.md sections i, k, o)"),
# line 51 GL1
(F,"| Cover glass `cover_glass` | GL1 | formed glass, 1.10 mm at the centre, rolls into the metal, black print outside the lit area with no opening (v7) |","| Cover glass `cover_glass` | GL1 | AGC Dragontrail Pro formed glass, 1.10 mm at the centre, rolls into the metal, black print outside the lit area with no opening (v7) |",LD+"'items 107, 108, 109' 04:15"),
(F,"| ADH1 | 0.10 mm optically clear adhesive, glass to screen over the whole face (17.30) |","| ADH1 | tesa 69404, 0.10 mm optically clear adhesive, glass to screen over the whole face (17.30) |",LD+"'item 96, rest (screen stack)' 04:15"),
(F,"| FOAM1 | 0.10 mm foam frame, 1.2 mm wide, closed all round (v7) |","| FOAM1 | 0.10 mm foam frame, 1.2 mm wide, closed all round (v7); Nitto SCF AN010, no adhesive, held by the screen's pressure |",LD+"'item 96, rest (screen stack)' 04:15"),
# line 55
(F,"| 27.2 x 12.6 x 0.3 mm, 6 layers, parts on the under face only |","| 27.2 x 12.6 x 0.3 mm, 4 copper layers with laser microvias, parts on the under face only |",LD+"'7, 11 (part), W2' 2026-11-13 00:39"),
# line 57
(F,"3.0 V regulator from the cell for the motor, 10 uF in and out, under the board beside the +Y floor slot","3.0 V regulator from the cell for the motor, 10 uF in (C83) and 4.7 uF out (C84, Murata GRM155R61A475MEAAD), under the board beside the +Y floor slot",LD+"'sim finding 4 (item 41)' and 'sim finding 4, correction' 2026-11-13 01:23, 02:07"),
# line 59, 60
(F,"| foam rings OD 1.8, bore 1.0, three thicknesses |","| Nitto SCF foam rings OD 1.8, bore 1.0, no adhesive, three thicknesses (AN010 0.10, SCF400T 0.2, SCF400 0.3; start values) |",LD+"'item 74' 2026-11-13 04:15"),
(F,"| discs 2.0 mm, at most 0.10 thick, in the underside seats |","| discs 2.0 mm of Saati Acoustex 010a mesh on a ring of tesa 61305 (2.0 mm outside, 1.0 mm bore), stack 0.102 mm, in the 0.10 mm underside seats |",LD+"'item 73' 2026-11-13 04:15"),
# line 62 RC1
(F,"| Radio corner (only if the owner adopts it) | RC1 | resin corner of the body round the antenna |","| Radio corner | RC1 | resin corner of the body round the antenna, Master Bond EP30Med, cast on its own and bonded before the board goes in (the lead's default of 2026-11-13; the owner can overrule) |",RC),
# line 63 coating
(F,"coated gloss black with the body, bonded in the round 5.60 opening with DP420 Black |","coated gloss black with the body (Oerlikon Balzers BALINIT DLC, 1 to 3 um), bonded in the round 5.60 opening with 3M Scotch-Weld DP420 Black |",LD+"'items 105' and 'item 45'"),
# line 75, 76
(F,"| die-cut seal ring 0.05 mm thick in the body's glass seat, lowered 0.05 mm; tape not chosen |","| die-cut ring of tesa 61305 double-sided film, 0.05 mm thick, in the body's glass seat, lowered 0.05 mm |",LD+"'item 110' 2026-11-13 04:15"),
(F,"| Floor slot sealant | none | no part number and no part in the model; the need is open item S26 |","| Floor slot sealant | none | 3M Scotch-Weld DP420 Black, the adhesive of the joystick frame, ordered by its name and the 50 ml cartridge size as its sheet prints them (no 3M number in a saved document); no part in the model; also SEAL2 (US 7 to 9) |",LD+"'item 45' and 'adhesive code, switch code, screw' 04:15"),
# line 84
(F,"Steps that change if the owner adopts the resin radio corner (`design/architecture.md:674`) carry a line \"Radio corner:\". The procedure is written for the one-piece metal body, which stays the design until the owner decides (`design/architecture.md:676`).","Steps that change because of the resin radio corner (`design/architecture.md:674`) carry a line \"Radio corner:\". The resin corner RC1 is in the design (the lead's default of 2026-11-13, which the owner can overrule, `design/architecture.md:676`): the body is the metal part with that corner cut away, and RC1 is its own part.",RC),
# line 89, 90
(F,"the outline 27.2 x 12.6 mm and the antenna notch 1.8 x 3.6 (`design/mfg/specs/main-board.md:27`, `design/mfg/specs/main-board.md:31`).","the outline 27.2 x 12.6 mm and no notch (`design/mfg/specs/main-board.md:27`, `design/mfg/specs/main-board.md:31`).",M9+" row assembly.md line 89"),
]
