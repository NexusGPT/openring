# W11 open mechanical items: values that would close them

Started: 2026-11-13 03:30 CET (from `date`). Scope: the 25 open W11 rows of design/wiring/deferred-triage.csv (numbers 36, 45, 48, 53, 73, 74, 77, 78, 85, 95 to 103, 105 to 110, 160). Item texts are copied from the Item column of design/wiring/deferred-items.md. Project file lines were read as they stood at that time; I never run git, so the commit was not checked. Each option is a proposal for the lead; nothing here is decided.

Reading rules used: a maker fact is cited with the saved document in design/datasheets/w11v_*.pdf (page and line of its saved text). A part code appears only where a saved maker document shows it. Values only a built unit can show are marked "start value, to measure", not proven. Logs of the runs, and the text copies of the PDFs used for page and line numbers, are in the scratchpad folder w11v, not in the project. Web requests: at most 8 per item (the count per item is in the run notes, not in the project).

## Item 36
1. Item: 36, "Liner made as a laminate with the two ribbons inside it: can it be made, and how is it repaired (S19)."
2. Today:
   - Liner: a 0.3 mm skin of skin-safe resin cast in place over the parts; the two flex ribbons (1.4 x 0.15 mm) are embedded with 0.075 mm of resin each side. design/mfg/specs/band-liner.md:6; ribbon row at band-liner.md:59.
   - Ribbon stack-up: polyimide core 25 um, copper 12 um, coverlay both sides, finished 0.11 mm. design/mfg/specs/band-flex-tails.md:17. Radial allowance in the liner 0.15 mm: band-flex-tails.md:33.
   - Resin grade and supplier open (band-liner.md:43, open point 1); cure temperature and time open (band-liner.md:45, open point 3).
   - Conflict K-A5 (S19): the ribbons embedded with 0.075 mm of resin, "not proven by a single cast; no maker has built such a liner. The first bench housing measures it." design/mfg/specs/band-liner.md:52.
   - Repair is excluded by the assembly order: "Repair is not possible after casting" (design/mfg/assembly/assembly.md:253, which cites design/architecture.md:440; band-liner.md:15 says the same). This conflicts with S19's question "how is it repaired" (design/architecture.md:517), which the files leave unanswered. Searched "repair" in band-liner.md, architecture.md and assembly.md: hits at band-liner.md:15 ("Repair after casting is not possible"), architecture.md:440 (the same statement), architecture.md:517 (the S19 question), assembly.md:253 and assembly.md:318 (a boot loader fault cannot be repaired, not about the liner).
3. Maker facts:
   - Smooth-On Dragon Skin NV Series technical bulletin, saved as design/datasheets/w11v_smoothon-dragonskin-series-tb.pdf (address https://www.smooth-on.com/tb/files/DRAGON_SKIN_NV_SERIES_TB.pdf; text copy w11v_smoothon-dragonskin-series-tb.txt). Page 1, saved text line 12: "skin safe and certified by an independent laboratory" (no standard number is named). Page 1, line 58: the row "Dragon Skin 10 NV" shows 15 min and 75 min; I read these as pot life and cure time from the column layout (the text layer splits the column headers, so this reading is not certain). Page 1, line 71: "Warmer temperatures will drastically reduce working time and cure time."
   - Flex ribbon embedded in cast resin: no maker document found. Searched with one web query (skin-safe cast resin and potting data sheets). Hits: Sika UR 3558, Synflex Voltacast 3110, 3M Scotchcast 226; these are electrical potting resins and none states a skin-contact claim. Not found.
   - Skin-contact standard for the resin (ISO 10993 or USP Class VI) in the Smooth-On bulletin: not found.
4. Options:
   - Option A (measurement step, first): build one coupon before any liner tool. Embed a 60 mm piece of the ribbon stack (band-flex-tails.md:17) in a 0.3 mm skin of the chosen resin, with 0.075 mm each side, cured as the maker says. Cut a section and read the resin over each face with a 10x loupe and a rule, or under a microscope. Expected reading: at least 0.075 mm on each side and no void over the copper. Outside that: the coupon fails and Option C applies. Cost: a flex order for a few coupons and a resin kit; risk: the coverlay-to-resin bond is not in any document.
   - Option B (fixed start values, silicone test): 0.3 mm skin, 0.075 mm resin each side (already in the spec), and a platinum-cure silicone as the test material, since the Smooth-On bulletin calls its NV series skin safe. Start reference: Dragon Skin 10 NV, pot life 15 min and cure 75 min at 73 F (saved PDF, page 1, line 58). Cost: silicone is not the "resin" the spec names, so the spec wording changes; the cell's heat during cure must still be measured (band-liner.md:45).
   - Option C (design change, not decided): run the ribbons outside the liner in a channel. This changes the band channel and so the body spec and the outside shape; the S16 row already lists it as a choice (design/architecture.md:514).
   - Repair: the files exclude repair after the cast. A fixed answer is "no repair; a damaged liner is scrapped" (assembly.md:253). If the lead wants a repair, it must be a new step and needs its own coupon test; not tested here.
5. Your best reading: Option A, because the project's own K-A5 note says no maker has built this and no document settles it. Option C is the fallback if the coupon fails, and it changes the body.
6. Saved documents: design/datasheets/w11v_smoothon-dragonskin-series-tb.pdf (text copy in the scratchpad folder w11v).

## Item 45
1. Item: 45, "Motor window seal for US 7, 8 and 9 (S26 gains): sealant and method not settled; the ways out are not tried."
2. Today:
   - Open item S26 gains: "the seal of the motor window on US 7, 8 and 9 (sealant and method, with the floor slots; bench item B8)." design/architecture.md:810.
   - The seal is a part SEAL2, class polymer, of 0.79 to 0.81 cubic mm, about 4.0 x 1.1 mm, on US 7, 8 and 9 only; "same sealant and same step as the floor slots, before the cast"; sealant not chosen. design/mfg/specs/band-liner.md:65; band-liner.md:50 (point 8); assembly order step: design/mfg/assembly/assembly.md:233.
   - The window is the cut between the motor pocket and the block's cavity. design/mfg/specs/body.md:124. The SEAL2 volume is "the removed metal less the motor grown by 0.05". design/mech/thin/thin-notes.md:342 (Model v6.2 section, the SEAL2 row).
   - The motor glue line is 0.05 mm (motor_glue = 0.05, pocket floor below the motor). design/mech/thin/thin-notes.md:304.
   - The ways out (none tried): joystick about 2 degrees lower, a pocket wall under 0.30 accepted, a thinner motor, or an open pocket behind a glued cover. design/mech/thin/thin-notes.md:334.
3. Maker facts:
   - 3M Scotch-Weld DP420 Black technical data sheet, saved as design/datasheets/w11v_3m-dp420-tds.pdf (text copy in the scratchpad folder w11v). The copy was fetched from https://www.3market.cz/user/related_files/dp420-black-dp420ns-black-dp420-off-white-dp420lh.pdf because the 3M address returned HTTP 403 to curl. The copy is third party; its content is the 3M sheet (Page 1 of 10 footer at line 60). Page 1, lines 53 to 58: mix ratio 2:1 by volume, 2:0.97 by weight; worklife 15 min for 20 g mixed, 20 min for 10 g, 30 min for 5 g (73 F). Page 1, lines 41 to 42: base viscosity 20,000 to 50,000 cP. Page 1, lines 50 to 51: base 9.3 to 9.7 lb per gallon (CALC: 1.11 to 1.16 g/cm3 from 1 US gallon = 3785 cm3 and 1 lb = 453.6 g).
   - Page 2 (Shore D 75 to 80, cured): page 2, saved text line 96: "Shore D Hardness 75-80". Rigid: a structural epoxy, so it is not a flexible sealant.
   - A flexible sealant for the motor window: no maker document found. Not searched beyond this one (budget); the web search for DP420 returned the 3M product pages only.
4. Options:
   - Option A (fixed value, rigid): 3M Scotch-Weld DP420 Black, mixed 2:1 by volume (page 1 line 53). The order code is not shown in the saved copy, so no part code is given (the code rule). Start value: fill 0.80 mm3 (band-liner.md:65), about 0.9 mg (CALC from the density above). Risk: it is rigid (Shore D 75 to 80) in a 0.05 mm glue zone next to a vibrating motor; a crack is possible. Also it bonds to the coating (item 106). Cost: low, one cartridge set per dummy.
   - Option B (measurement step, before the choice is closed): build the printed dummy of US 9 (bench item B8), dispense the chosen sealant into the window with a 0.5 mm needle, let it cure, cut through the section and read the fill under a 10x loupe. Expected reading: the fill reaches the motor's back face with a 0.05 mm glue zone and no void over 0.1 mm. Outside that: the motor is not held or the seal leaks; choose a softer sealant or change the window (Option C).
   - Option C (design change, not decided): one of the thin-notes ways out (motor 2 degrees lower, wall under 0.30, or an open pocket behind a glued cover). Each changes a fixed decision in thin-notes.md:334; the lead decides.
5. Your best reading: Option B, because the sealant is rigid in a motor gap, so the lead needs the section read before the material is fixed; Option A is the start value to test. Option C is needed only if the section fails.
6. Saved documents: design/datasheets/w11v_3m-dp420-tds.pdf (text copy in the scratchpad folder w11v).

## Item 48
1. Item: 48, "Screen cable is 12.4 mm wide where the model folds 5.0 mm (K16); Tailor Pixels must answer whether a 5.0 mm cable can be made (S27)."
2. Today:
   - K16: "the screen maker's cable is 12.4 mm wide for 11.5 mm beyond the panel; the model folds a 5.0 mm cable in a 5.4 mm pocket, 0.6 mm from the antenna: not solved. A 12.4 mm fold does not fit beside the antenna." design/architecture.md:757.
   - S27: "The screen's cable is 12.4 mm wide at the fold; the body has a 5.4 mm pocket for it beside the antenna... Can the cable be narrowed to 5.0 mm from the bond on... the screen maker (Tailor Pixels)." design/architecture.md:525.
   - Fold room beside each slot: 2.6 x 2.2 x 1.03 mm free; the bend radius is the flex maker's. design/architecture.md:759; design/mech/thin/thin-notes.md:159.
   - The 12.4 mm and 5.0 mm figures are the project's; no file gives the bend radius of the screen tail (searched "bend", "fold", "radius" in the saved screen datasheets: no hit).
3. Maker facts: (Tailor Pixels TOH095XVT-01, 0.95 inch AMOLED; saved as design/datasheets/display_TOH095XVT-01.pdf, not copied again by me; the text layer is in the scratchpad copy):
   - Page 4, module outline: "12.8(H) x 27.35(V) x 0.8(T) mm"; page 4 note 1: "Excluding hooks, posts, FPC/FPC tail etc." (text layer line 104 and 122 of page 4).
   - Page 5 (mechanical drawing, read as an image): the tail is wide under the panel and narrows to the connector end, which carries 15 contacts; the callouts are 12.8, 12.2 (polarizer), 10.8 (active area), 20 (tail length from the panel edge), 4.8 (contact field), and "0.2 +/-0.03 含PI补强" (0.2 mm with PI stiffener). The drawing does not print the tail width. The 12.4 mm figure comes from a tool that measured the drawing's vector lines (design/mech/light-path/light-path.md:10 to 12: tail Y -6.198 to +6.204, so 12.40 mm); it is a reading, not a printed dimension. My scale from the drawing (CALC, image pixels): the connector neck is about 4.8 mm wide and the wide tail is about the panel width.
   - No bend radius, fold instruction or minimum fold height appears in the full text of display_TOH095XVT-01.pdf or in the two saved text copies (design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt, slim_toh095xvt-existing-p1-4.txt): the search for "fold", "radius", "bend" and "FPC" gave only the notes above. Not found.
   - Tailor's answer on a 5.0 mm cable: not in any document. Not found; this is the maker's question (S27), and this helper does not write to the maker.
4. Options:
   - Option A (measurement step, first, on a stock module if the owner has one): measure the wide tail at 3 points with calipers (the 12.2 to 12.8 band from the drawing). Expected: 12.2 to 12.8 mm, so the stock tail cannot be folded into the 5.4 mm pocket as it is (the model fits 5.0). Outside that: the sample is not the drawing; report the reading. Cost: one module and calipers; risk: none to the design.
   - Option B (fixed value, the supplier's answer): the cable at 5.0 mm wide, with the same 0.2 mm tail and 15 contacts, as a request for Tailor Pixels. The owner or the lead sends it; this helper does not. Until Tailor answers, 5.0 mm has no document, so the value is a request, not a fact.
   - Option C (design change, not decided): the body or the antenna changes so that the stock 12.4 mm tail folds (more pocket room). This changes the outside shape and the body spec, so the lead decides.
   - Fit numbers the lead can use now: the pocket is 5.4 mm, the cable 12.4 mm (project) or about 12.2 to 12.8 (drawing), so the stock tail is about 7 mm too wide for the pocket. CALC from the project's own numbers.
5. Your best reading: Option B with Option A in parallel, because the stock tail is about 2.3 times the pocket width and no fixed value can close it inside the current body. Option C is the fallback if Tailor says 5.0 mm cannot be made.
6. Saved documents: none new for this item; the cited screen datasheet is design/datasheets/display_TOH095XVT-01.pdf (existing copy). Text copies in the scratchpad: w11v/toh-full.txt.

## Item 53
1. Item: 53, "Metal on the screen ledge over the antenna (S24) and the ledge glass clear check (S25, S-L1): the screen maker answers."
2. Today:
   - S24: "Metal on the screen panel's ledge over the antenna, X -13.675 to -10.6, Y 2.05 to 6.4 (17.20); and the owner's decision on the resin radio corner." design/architecture.md:522. Open item text: design/architecture.md:682.
   - S25 is marked two ways. design/architecture.md:523 says "S25 CLOSED by 17.30 (the recording light, LED1, the light guide LG1 and the board hole are removed in v7; no supplier is asked)". The older open text is at design/architecture.md:698 ("the screen maker confirms the ledge glass is clear at X -12.625 to -12.225, Y -3.150 to -2.750"). The light path notes still list the ledge spot as open S-L1: design/mech/light-path/light-path.md:117 and the row at light-path.md:64. The LP1 light plug is removed in v7 (light-path.md:60). So the S25 check is for a part that v7 no longer has; the conflict is for the lead.
   - Tail on the ledge (measured from the maker drawing by a vector tool, not printed): ledge 2.951 mm from the panel end, X -13.675 to -10.724; bond fingers X -13.574 to -12.775; the tail lies on the glass from X -13.675 to -12.775, Y -6.198 to +6.204. design/mech/light-path/light-path.md:9 to 12 (tool output logs/screen_ledge.log, not saved here).
   - K17 (driver chip on the ledge): "removed from the model, the maker's drawing shows none; the screen maker confirms with S25." design/architecture.md:758.
3. Maker facts:
   - Tailor Pixels TOH095XVT-01 drawing, page 5 (saved as design/datasheets/display_TOH095XVT-01.pdf; I read it as an image). The drawing shows the tail under the panel and no chip on the ledge; it does not show the metal on the ledge or the fan-out. Not found: a fan-out or metal layout for the ledge in any saved document.
   - Page 4 of the same datasheet: "Driver IC: SH8501A" (text layer, the features table; the saved text line is in the scratchpad copy toh-full.txt). The datasheet does not say where the driver sits. Not found: location of the driver on the glass.
   - No other maker document for the screen exists in the datasheets folder: the file-name search for "toh" and "tailor" gave the four Tailor files (display_TOH095XVT-01.pdf and three slim_ text copies).
4. Options:
   - Option A (fixed design rule, no maker needed to start): no metal on the ledge in X -13.675 to -10.6, Y 2.05 to 6.4 (the S24 window; 3.08 x 4.35 mm, CALC from the S24 numbers). Check: the bond fingers (X -13.574 to -12.775, Y -5.805 to +5.805, light-path.md:11) overlap the S24 window in X and in Y from 2.05 to 5.805, so the rule as written conflicts with the bond on the drawing. The fingers are the screen's own metal; the rule cannot be met without the maker. Risk: the maker's real fan-out may not match the drawing.
   - Option B (measurement step on a stock module, if the owner has one): with a backlight, look at the ledge at 10x through the glass; mark the S24 window (X -13.675 to -10.6, Y 2.05 to 6.4, measured from the tail end, not from the glass edge). Expected reading: no metal, no chip, no tape in the window. Outside that: the metal is over the antenna; apply Option C. Cost: one module, loupe.
   - Option C (design change, not decided): move the antenna or keep a 0.30 mm no-metal margin; the antenna maker's layout decides, and the lead decides.
   - S25: the only use of the S25 check was the recording light, which v7 removed (architecture.md:523). A fixed answer for S25: close it as "not needed in v7", so only S24 stays open. The lead must confirm, since architecture.md:698 still reads open.
5. Your best reading: Option A as the fixed rule plus Option B on a stock module, and close S25 as removed by 17.30 once the lead confirms it, because the light path it checked is gone. The maker still has to confirm the ledge layout in writing.
6. Saved documents: none new; the cited drawing is the existing design/datasheets/display_TOH095XVT-01.pdf.

## Item 73
1. Item: 73, "Microphone seal and membrane (at most 0.10 mm): no part chosen (Gore to quote)."
2. Today:
   - Membrane disc 2.0 mm, at most 0.10 thick, in a seat on the block's underside; "no part chosen". design/architecture.md:58 (Gore "to quote"; loss to measure, bench B7).
   - O4: "Membrane at most 0.10 thick: no part chosen; Gore action 12.6 changes." design/mech/mic-path/mic-path.md:201.
   - Membrane seat: counterbore Ø2.00 x 0.10 deep (Z 0 to 0.10); membrane "hydrophobic acoustic membrane disc (ePTFE class) with an adhesive ring... at most 0.10 thick with its adhesive", marked [ESTIMATE]. design/mech/mic-path/mic-path.md:73 and :74.
   - Earlier version used a GAW112 membrane of 0.24 mm: design/mech/mic-path/mic-path.md:161 (quoting architecture.md line 60 before 17.19).
   - O3, the 0.20 mm metal ring under the seat, is item 77, not repeated here.
3. Maker facts:
   - Gore Acoustic Vents GAW111 and GAW112 data sheet, saved as design/datasheets/w11v_gore-acoustic-vents-gaw111-gaw112-datasheet.pdf (fetched from https://www.gore.com/sites/default/files/resources/pdf/2026-09/gore-protective-vents-dust-splash-a4-datasheet-en.pdf.assetdownload.pdf, linked from https://www.gore.com/resources/data-sheet-gore-acoustic-vents-portable-electronic-series-gaw111-and-gaw112-dust-and). Page 5, product table:
     - Material "Cellulose/PET-Nonwoven & dark gray" (saved text, page 5 line 144); not ePTFE.
     - Reference thickness: GAW111 0.18 mm, GAW112 0.24 mm (page 5 line 148). Footnote c: "Nominal aggregate thickness of adhesive and PET nonwoven layers. Actual thickness may vary due to the compressibility of materials." (page 5 line 188 to 190).
     - Adhesive type acrylic (page 5 line 153). Average acoustic impedance (200 to 5000 Hz) GAW112 105 rayls MKS (page 5 lines 138 to 139); maximum transmission loss under 2 dB at 200 to 5000 Hz (page 5, the "Maximum transmission loss" row, saved text line 141).
     - Standard round parts start at a 3.0 mm transducer with 8.0 mm outer (GAW1120308, page 5 line 166). Custom part designs are quoted by Gore for size, adhesive and thickness (page 5 lines 181 to 187).
     - So: no part at or under 0.10 mm, and no 2.0 mm disc, in this data sheet. The ePTFE class with 0.10 mm is not in any saved document. Searched: one web query for GAW112 thickness; the GAW334 data sheet URL returned 404 twice (not saved).
   - Gore's own answer (action 12.6, O4) is not in any saved document. Not found.
4. Options:
   - Option A (measurement step on a bench sample, bench B7): take the closest Gore vent in the saved data sheet, GAW112 (0.24 mm, 105 rayls), cut a 2.0 mm disc, and measure the loss through the bore, gasket and membrane as bench B7 says (mic-path.md:154). Expected: transmission loss within the budget that mic-path.md sets (O6: SNR falls from 67.5 to 64.5 dB(A), mic-path.md:203); a loss under 2 dB at 200 to 5000 Hz is the Gore table figure for GAW112 (not a figure for the 2.0 mm disc in this stack). Outside that: the membrane is too stiff or too thick; go to Option B.
   - Option B (fixed value from Gore, requested by the owner or lead): a custom GAW112-type disc at the 0.24 mm reference thickness (Gore quotes custom sizes, page 5 lines 181 to 187; the bore and disc diameters are for Gore to quote). The seat depth would follow it: about 0.25 mm if the seat matches the disc with 0.01 mm margin (a choice, not a Gore value). The seat is in the block underside, so the body spec changes; the lead decides. This is the only Gore family in the saved data sheet that fits a membrane of this type; the ≤0.10 limit has no source.
   - Option C (design change, not decided): keep the 0.10 limit and look for an ePTFE vent at 0.10 mm from Gore or another maker; no saved document yet, so this is open.
   - Cost and risk: A needs a bench rig; B needs a seat change and a Gore quote; C has no source yet.
5. Your best reading: Option A to measure the real loss on the 0.24 mm vent before the seat is fixed, then Option B if the loss is in budget, because the ≤0.10 mm limit has no document behind it.
6. Saved documents: design/datasheets/w11v_gore-acoustic-vents-gaw111-gaw112-datasheet.pdf

## Item 74
1. Item: 74, "Gasket foam material and its three thicknesses are estimates; a gasket maker must answer."
2. Today:
   - Gasket: "ring of soft closed-cell foam (polyurethane or silicone class) with pressure-sensitive adhesive on both faces; OD 1.80, bore 1.00, fills the gap from the pocket bottom (Z 0.300) to the lid: 0.13 nominal, 0.03 with the tallest part, 0.23 with t..." design/mech/mic-path/mic-path.md:70 (row 2 of the table).
   - Thickness per unit is an estimate: "after reflow, measure the lid height below the board's under face, compute the gap g = lid Z - 0.300, and choose a gasket of free thickness 0.10 (g under 0.07), 0.20 (g 0.07 to 0.14) or 0.30 (g over ..." design/mech/mic-path/mic-path.md:152, labelled "[ESTIMATE, all three numbers]".
   - O2: "Gasket material and the three thicknesses: [ESTIMATE]; a gasket maker and bench B7 settle them." design/mech/mic-path/mic-path.md:199.
   - The assembly order lists the gasket as open: "Microphone gasket foam and its three thicknesses | 3, 12 | a gasket maker; bench B7 | S23". design/mfg/assembly/assembly.md:370.
   - The leak with a gasket open is 7.31 times the bore's impedance at 1 kHz, so the gasket must seal (mic-path.md:150).
3. Maker facts:
   - Rogers PORON 4701-40 Soft data sheet (copy hosted by Mueller-Ahlhorn), saved as design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf (fetched from https://mueller-ahlhorn.com/wp-content/uploads/2024/11/PORON-4701-40-Soft_ENG.pdf). Page 2, lines 57 to 58 of the saved text: thickness ranges by density group: 3.18 to 12.70 mm, 1.57 to 3.18 mm, and 0.79 to 1.14 mm (tolerance plus or minus 10 or 20 percent). So this family has no sheet at 0.10, 0.20 or 0.30 mm; its thinnest is 0.79 mm (CALC from the lines above). Its compression set and force rows are on page 2 near line 63 and 71 (the 4701-40 values, not for the chosen part).
   - Searched once for PORON 4701 adhesive-backed sheets (web). The results gave a 0.51 mm PSA product (4701-SG+RL) from a converter's page, not a Rogers data sheet, so it is not used here. Not found: a maker sheet for a foam gasket at 0.10, 0.20 or 0.30 mm with pressure-sensitive adhesive.
   - Knowles SPK0641HT4H-1 (the microphone): "the recommended Gasket Cavity Diameter is D ≥ 1.0 mm and the recommended Case Hole Diameter is 1.0 ≤ D ≤ 1.5 mm" (saved copy design/datasheets/w1_knowles_spk0641ht4h-1_chipsmall.pdf, page 6, text line 369). The bore 1.0 is at the minimum of this range.
4. Options:
   - Option A (measurement step, first): on the printed dummy (bench B7, mic-path.md:154), measure the lid height below the board's under face at the microphone position after reflow, with a depth gauge or calipers, and compute g = lid Z - 0.300 as mic-path.md:152 says. Expected reading: g between 0.03 and 0.23 mm (mic-path.md:70). Outside: a gap over 0.23 needs a different foam; under 0.03 the gasket is over-compressed, and the lid or the gasket must change.
   - Option B (fixed value, a sheet from a maker): a thin PSA foam at 0.10, 0.20 or 0.30 mm free thickness from a gasket maker, with its own data sheet; no part code is given, because no saved document shows one. The PORON 4701 sheet above is too thick (0.79 mm minimum) for a 0.13 mm gap, so it is not an option.
   - Option C (design change, not decided): thicken the gap by changing the lid or the pocket depth; this changes the body spec (pocket floor Z 0.300) and so the lead decides.
   - Cost and risk: A costs one dummy and a gauge; B needs a gasket maker's quote, and no code is known yet; C changes a fixed value.
5. Your best reading: Option A now, because the gap is measured on the first dummy and it fixes the thickness; Option B needs a gasket maker, and the PORON family in the saved document cannot reach 0.10 to 0.30 mm.
6. Saved documents: design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf (and its text copy in the scratchpad, not in the project).

## Item 77
1. Item: 77, "0.20 mm metal ring under each membrane seat is an open point (O3)."
2. Today:
   - The ring: "The ring between the seat and the pocket, from Ø1.0 to Ø2.0, is 0.20 thick (check.log C26w). That is under the 0.30 stack floor of R4 in that ring only. No project rule covers a local web; the body maker must accept it (open item O3)." design/mech/mic-path/mic-path.md:79.
   - The check log: "C26w.mic_1 INFO metal web between the membrane seat (Z 0 to 0.1) and the pocket bottom (Z 0.30): 0.20 mm over a ring from d 1.0 to d 2.0; below the 0.30 stack floor of R4 in this ring on..." design/mech/mic-path/check.log:31; the same for mic_2 at check.log:35.
   - The seat is "Ø2.00 x 0.10 deep (Z 0 to 0.10)" (mic-path.md:73). The pocket floor is at Z 0.30 (mic-path.md:70).
   - O3 in the open list: design/mech/mic-path/mic-path.md:200. S23 lists "the 0.20 mm metal ring" as open with the body maker: design/architecture.md:662.
   - The body is CNC from bar (design/mfg/specs/body.md:17, "Default, to confirm with the maker"), so the ring is machined, not moulded.
3. Maker facts:
   - No maker document for a titanium CNC minimum web is saved or found in the datasheets folder (the folder has no body-maker file; the body maker is not named in the files).
   - One web search (titanium CNC minimum wall) gave machine-shop blog rules of thumb only: about 0.5 mm for isolated ribs and 1.0 mm for unbraced walls, depending on height. These are blog figures, not a maker's data sheet, so they are not saved and not used as a value here. Not found: a maker's own number for a 0.20 mm web in titanium.
4. Options:
   - Option A (fixed value, in the model): raise the web to the R4 floor of 0.30, which means the pocket floor moves from Z 0.30 to Z 0.40 or the seat is deepened (the seat is Z 0 to 0.10 now). This changes the body stack, so the lead decides. Cost: a 0.10 mm change in the pocket floor, which the mic-path and the gasket (item 74, the gap 0.03 to 0.23) must follow.
   - Option B (measurement step on the first machined body): with a micrometer or a depth gauge through the pocket at 4 angles on the ring, read the web from the pocket floor to the seat bottom. Expected reading: 0.20 mm, within the tolerance the body maker quotes. Outside (for example under 0.15 mm, or any hole through): the body maker must change the web (Option A). Cost: one machined body; the check needs a body first.
   - Option C (no change): accept the 0.20 mm web and ask the body maker to confirm in writing; this is the open point O3 as written. Risk: a thin web on a titanium part can chatter or break in machining (the blogs say so, not a maker's document).
5. Your best reading: Option A, because the project's own rule R4 sets 0.30 and the web is below it on purpose only by a local exception that no document supports; Option B is then the check on the first body.
6. Saved documents: none for this item.

## Item 78
1. Item: 78, "Thumb side: conflict K8, no opening in a side wall; whether a finger or thumb covers the opening (O5) is not known."
2. Today:
   - K8 is closed: "no microphone opening in any wall (check4 mic lines; the exterior has none: merged32f-report.md line 41)." design/mech/thin/thin-notes.md:149. The earlier K8 text (slots on the joystick side where the thumb works) is at thin-notes.md:92.
   - The openings are in the block's underside: "the 1.0 mm open centre of the membrane seat, on the block's underside, at X -11.770 and +11.770, Y -4.800" design/mech/mic-path/mic-path.md:75. The thumb note: "there is no opening in a side wall... Whether the thumb or the next finger covers them in use is [ESTIMATE] and goes to bench B7." design/mech/mic-path/mic-path.md:83.
   - O5: "Whether the finger, the thumb or the next finger covers the openings while worn: [ESTIMATE], bench B7." design/mech/mic-path/mic-path.md:202.
   - The sound enters from the gap between the block and the back of the finger: 0.4 mm on the centre line and 1.7 mm at the holes, for a round finger [ESTIMATE]. design/architecture.md:658. "NOT PROVEN: how well the ring hears a room through openings that face the finger." design/architecture.md:659.
   - The noise budget: SNR 64.5 dB(A) with this path against 67.5 dB(A) before. design/architecture.md:658; O6 at design/mech/mic-path/mic-path.md:203.
3. Maker facts:
   - Knowles SPK0641HT4H-1 datasheet (saved as design/datasheets/w1_knowles_spk0641ht4h-1_chipsmall.pdf), page 8, text line 471: "Do not insert any object in port hole of device at any time." This is about the microphone port itself, not a finger over the room opening, so it does not decide item 78.
   - The Knowles note on the acoustic port refers to a SiSonic design guide for port size (text line 370 of the saved copy); that guide is not in the datasheets folder. Not found: a maker number for a finger or thumb covering a room opening.
4. Options:
   - Option A (measurement step, bench B7, first): build a US 9 printed ring with the block and the two openings as drawn, fit it on a finger-sized mandrel of the US 9 inside diameter (18.95 mm, band-liner.md:30 table), and place a reference loudspeaker 1 m away. Record the level with the openings open, then with a finger pad and a thumb pad pressed on the openings, and with the hand gripping an object. Expected reading: the level drop with a covering finger stays within the 3 dB of the O6 budget (67.5 to 64.5 dB(A)). Outside (more than 3 dB drop): the ring hears poorly when worn; go to Option B. Cost: one printed ring, a loudspeaker, a sound level meter; the 3 dB limit is the project's O6 figure, not a standard.
   - Option B (design change, not decided): move the openings to where the finger does not reach (the underside has no such place; the second-best path has about 1,000 times the flow resistance, architecture.md:659). This changes the microphone place, so the lead decides.
   - Option C (fixed value, a spacer): a 1.7 mm finger gap at the holes is already the best case [ESTIMATE, architecture.md:658]; no spacer is in the design, so this is not a value to fix now.
5. Your best reading: Option A on the printed ring, because the finger cover is the open question and only the wearing test answers it; Option B is needed only if the drop is over 3 dB.
6. Saved documents: design/datasheets/w1_knowles_spk0641ht4h-1_chipsmall.pdf (existing copy, cited for page 8 line 471).

## Item 85
1. Item: 85, "Holder: the moulder has not confirmed the 0.79 mm walls between bores in LCP."
2. Today:
   - "Holder: the moulder has not confirmed the 0.79 mm walls between bores (0.794 mm, the bores dia 1.60 at 2.39 mm centres) in LCP, the stake strength is not tested, and the touch electrode E1 now reads through a 1.97 mm LCP wall (bench B3)." design/case/c5d-open-points-handover.md:44.
   - The holder carries the spring pins P1 to P4, which the case notes call "one part, Harwin P70-6000045R" (design/case/r3-fix-notes.md:5); the pin is "still proposed, not confirmed (conflict K1: stroke not in the files read)" (design/case/c5d-open-points-handover.md:43).
   - Material: LCP (design/case/c5d-open-points-handover.md:44). Mould and moulder are not named in that line.
3. Maker facts:
   - Harwin P70 data sheet, saved copy design/datasheets/p3_harwin_p70.txt: PCB holes Ø1.10 to Ø1.20 (lines 69 to 73). These are the board holes of the pin, not the holder bore of 1.60 mm, so the P70 sheet does not give the holder's wall.
   - LCP wall guidance: one web search (Celanese Vectra design guide) did not return the Celanese guide itself. Hits were blogs: a 0.3 to 1 mm wall range (Fictiv), and a Vectra MT result with 0.2 mm walls for a flow length (not a minimum). None is a maker document; none is saved or used as a value. Not found: a maker's minimum wall or hole-to-hole wall for LCP.
   - The moulder's answer is the only maker fact that closes this item; it is not in any saved document.
4. Options:
   - Option A (measurement step, first sample): print or mill a holder at the same size in the same layout, and cut one section through the 0.79 mm wall between two bores with a saw or a knife; read the wall with calipers on the section. Expected reading: 0.79 mm within 0.05 mm. Outside (under 0.70 mm, or a crack in the section): change the holder layout (Option B). Cost: one holder sample; this tests the printed or machined part, not the LCP moulded one, so the moulder's sample still needs the same check.
   - Option B (fixed value, layout change): move the bores to 2.6 mm centres, which gives a wall of 1.0 mm (CALC: 2.6 minus 1.6 bore). This changes the case layout and the pin positions, so the lead decides.
   - Option C (fixed value, from the moulder): the moulder's written confirmation that a 0.79 mm LCP wall between two 1.60 mm bores can be moulded, with the stake test. This is a request for the owner or lead to send; this helper does not write to a supplier.
   - Cost and risk: A is cheap but tests another material; B changes the case; C needs the moulder's answer and no document yet exists.
5. Your best reading: Option C is the one that closes the item, so the lead should send it with the B fallback in hand; Option A gives an early reading on the sample.
6. Saved documents: design/datasheets/p3_harwin_p70.txt (existing copy, cited for lines 69 to 73).

## Item 95
1. Item: 95, "Straight lift-out is not simulated; the other case pictures are C5c renders, not re-rendered."
2. Today:
   - "The ring is checked in its seated pose, turned (roll), and against the swinging lid; the straight lift out is not simulated as a motion." design/case/c5d-open-points-handover.md:45.
   - "The other pictures (side, underside, in-hand, compare) are the C5c renders; the outside did not change." design/case/c5d-open-points-handover.md:46.
   - The case sequence has the ring lifted after the lid swings open: "Lid swung open and ring lifted: touch reading falls, USB detach: EN low, OTG off, U1 back to Deep-sleep." design/case/case-architecture.md:147.
   - The joystick clearance result: "smallest 0.514 mm at US 13" from design/case/c5d-open-points-handover.md:49 (the RESULT line).
3. Maker facts: none; this is a fit question inside the project, so no maker document applies. Not applicable.
4. Options:
   - Option A (measurement step, physical, first): print the case and one ring at US 9, then at US 7 and US 13 (the two ends), open the lid to its stop, and lift the ring straight up with no turning. Read: the ring must come out with no touch, and a feeler gauge at the three nearest walls must read at least the clearance the design states (the joystick gives 0.514 mm at US 13; the other walls have no stated figure, so the first reading sets it). Outside (the ring catches a wall or the lid): record which wall and the depth of the catch; change the wall or the angle (lead decides). Cost: prints and a feeler set; risk: a print may differ from the model by its own tolerance.
   - Option B (fixed value via the model check): run the project's case check with a straight-up motion added as a step (the case check "case_check PASS 3447 pairs" is named at design/case/c5d-open-points-handover.md:49), and accept a pass with no pair closer than 0.3 mm (a fixed value [ESTIMATE]; the project's own pair threshold is not in the file I read). Cost: a script change in the case folder, which is not mine to change; it is the case helper's job.
   - Option C (cosmetic, not needed to close the fit): re-render the four pictures; no value depends on it. Cost: render time only.
5. Your best reading: Option A, because a printed ring in a printed case is the only test that shows a real straight lift; Option B is the cheaper route if the case helper can add the motion.
6. Saved documents: none for this item.

## Item 96
1. Item: 96, "Body spec open point 5 values (board, foam, adhesive, liner, flex stack) and open point 2 values are not settled."
2. Today:
   - The body spec points to "open point 5" for the board thickness 0.30 mm (design/mfg/specs/body.md:39), the foam pad 0.10 mm (body.md:40), the clear adhesive 0.10 mm (body.md:42), the liner 0.3 mm (body.md:45) and the joystick flex 0.15 mm (body.md:48). The "Open points" list (body.md:111, point 5) says: "Tighter than ISO 2768-f anywhere, inspection method, sampling plan: the maker proposes, the design partner accepts." So the pointer does not match the list: point 5 is about tolerances, not about these values. Found by reading body.md's open-points section.
   - Open point 2 is the screen pocket clearance: "Pocket clearance and depth for the screen panel (architecture 16.1 says 0.15 mm per side; the model uses 0.05): the design partner answers, then the maker confirms." design/mfg/specs/body.md (Open points, item 2); the pocket depth is "open point 2" at body.md:69.
   - The flex stack is in design/mfg/specs/band-flex-tails.md:17 (polyimide 25 um, copper 12 um, coverlay, finished 0.11 mm), which cites a JLCPCB flexible PCB page "fetched 2026-11-13" (band-flex-tails.md:17).
   - The liner: 0.3 mm resin skin, thickness open (design/mfg/specs/band-liner.md:6 for the skin; open point 5, "Tolerance of the thickness and inner diameter: the maker proposes", is at design/mfg/specs/band-liner.md:47).
3. Maker facts:
   - Board: JLCPCB rigid FR4 thicknesses are "0.4/0.6/0.8/1.0/1.2/1.6/2.0 mm" (saved copy design/datasheets/w5_jlcpcb_capabilities.html; canonical address https://jlcpcb.com/capabilities/pcb-capabilities; text line 1313 after removing tags). The 0.30 mm board is below the lowest listed option (0.4 mm). Not found: a 0.30 mm option anywhere in that page.
   - Flex stack: the page cited by band-flex-tails.md:17 was not reproduced. I fetched https://jlcpcb.com/capabilities/flexible-pcb-capabilities (saved copy not kept); its text is heaters and rigid rules, with no stack table. Not found: a saved flex stack-up from a maker.
   - Foam 0.10 mm and clear adhesive 0.10 mm: no maker document saved or found in this run (not searched beyond this list, budget). The Rogers PORON 4701-40 sheet (design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf, page 2 lines 57 to 58) starts at 0.79 mm, so it cannot give a 0.10 mm foam.
   - Liner: no maker value; the spec says the resin grade is open (band-liner.md:43).
4. Options:
   - Option A (fixed values, now): board 0.4 mm (the nearest JLCPCB FR4 option at or above 0.30; the cavity would need 0.10 more height, which the stack at body.md:42 does not have, so this is a change to the stack and the lead decides); foam 0.10 and adhesive 0.10 kept as start values, each to be confirmed by a measurement; liner 0.3 kept; flex stack kept at 0.11 finished (band-flex-tails.md:17).
   - Option B (measurement step, first article): measure each layer on a sample: board thickness with a micrometer at 3 points (expected 0.30 mm at the thinnest option, or 0.4 if the fab gives it); foam and adhesive with a micrometer on a stack of 10 pieces divided by 10 (expected 0.10 mm each); flex with a micrometer at 5 points (expected 0.11 mm, 0.21 under the stiffener, band-flex-tails.md:32). Outside that: the stack in the body changes and the lead decides.
   - Option C (fix the pointer): change "open point 5" in body.md to the right open-point numbers. This is a text fix, not a value.
   - Screen pocket (open point 2): fixed start value 0.05 mm per side as the model uses (body.md open point 2); the architecture's 0.15 mm (cited in the body spec) is the other value; measure on the first body with a plug gauge (expected: the panel slides in with 0.05 mm each side).
5. Your best reading: Option B with the start values in Option A, because the board's 0.30 mm is not a fab option and only a first article fixes the stack; the pointer error in Option C should be fixed in the same edit.
6. Saved documents: design/datasheets/w5_jlcpcb_capabilities.html (existing copy, cited for line 1313 of the text); design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf.

## Item 97
1. Item: 97, "Body model values to confirm, not in the architecture, taken from the 3D model."
2. Today:
   - The section lists the values taken from the 3D model (thin-notes section "Model v5", US 9): "Model values to confirm (not in the architecture, taken from the 3D model...)". design/mfg/specs/body.md:88.
   - The first one: "Floor slots 2.0 x 0.6 at Y = +-5.9, from X = -3.5 to X = -1.5 (two; model v6.2...)". design/mfg/specs/body.md:89. Also in that line: the motor window "about 4.0 x 1.1 mm", closed by SEAL2.
   - The same values per size are in the body's data file for each size: body-us7.dims.csv lists the floor slots 2.0 x 0.6 (X -3.5 to -1.5, Y +-5.9, Z -0.20 to 1.00), the motor window 4.009 long x 1.049 high, the cable fold pocket 0.55 x 5.4 x 2.0 (design/mfg/parts/body/body-us7.dims.csv, rows "Floor slots (2)", "Motor window", "Cable fold pocket").
   - The "What to inspect" list at body.md:92 names the first-article checks: block length, width, heights, floor thickness, band inner diameter, shoulder thickness, shell wall, joystick opening 5.60 with a pin gauge.
3. Maker facts: none. The values come from the project's own model, so no maker document applies. Not applicable.
4. Options:
   - Option A (measurement step, first article, US 9 first): with calipers and a depth gauge, read the two floor slots (length 2.0, width 0.6, from the top at Z -0.20 to 1.00 per the dims file) and the motor window (4.0 by 1.1, body-us9 dims). Expected reading: each within the ISO 2768-f tolerance the body spec sets for the floor slots (the tolerance for the floor slots is ISO 2768-f, body.md:23). Outside that: the model value is wrong; fix the model and reissue the STEP.
   - Option B (fixed value by checking the STEP against the dims file): run a script that reads the STEP bounding box and the per-size dims (the index in design/mfg/parts/index.csv lists the box of each size) and compares it with the dims values. Expected: the same numbers to 0.01 mm. Outside: the STEP and the dims disagree; the model owner decides which is right. Cost: a short script; no part is bought.
   - Option C (keep as is): accept the model values as the start values with a note. This is the status quo.
5. Your best reading: Option A on the first article with Option B as the cheap check before it, because the model values are the only source for these numbers and a first article is the only test of them.
6. Saved documents: none for this item.

## Item 98
1. Item: 98, "Body variants for sizes other than US 9: the per-size values are not in the body spec."
2. Today:
   - The body spec now has the per-size table: "Per ring size values (model v6.2; ...)" with one row per size US 7 to 13 (joystick angle, pocket roof, motor angle, floor slot bottom, motor window, metal round the opening). design/mfg/specs/body.md:123 (section header) to body.md:134 (US 13 row); the table's first row is US 7 at body.md:128.
   - The per-size STEP and dims files exist for all seven sizes, listed in design/mfg/parts/index.csv (body US 7 at line 22, US 8 at line 34, US 9 at line 2, US 10 at line 46, US 11 at line 57, US 12 at line 68, US 13 at line 79; each with a STEP row and an STL row). The per-size drawings exist: design/mfg/drawings/body-us7.pdf to body-us13.pdf (US 9 is body.pdf).
   - The spec's own text still says the per-size values are "in the last section" and that "the maker takes them from the STEP file per size once the parts helper exports it" (body.md:113). The export is done (index.csv), so that sentence is out of date. Found by reading body.md:113 against the index.
   - The body spec's "Ring sizes" table gives inner diameters for US 5 to 13 (body.md:99): US 7 17.32, US 13 22.20 mm [CALC].
3. Maker facts: none needed for the values (they are the project's model). Not applicable; the maker's own answer on the body variants is open point 7 (body.md:113).
4. Options:
   - Option A (fixed value, the spec as it stands): the per-size table at body.md:126 to 134 is the value set; close item 98 by stating that the table and the index are the values and that body.md:113 is updated to point to them. Cost: an edit of body.md (not mine to change; the lead or the spec owner does it).
   - Option B (measurement step, per size, on the first article of the smallest and largest size): the band inner diameter with a ring gauge (plug) at US 7 and US 13; the expected readings are 17.32 and 22.20 mm (body.md:99) within the tolerance the spec gives (ISO 2768-m, plus-only open point 6). Outside that: the size's inner diameter is wrong; the lead decides. Cost: two machined bodies or two plug gauges.
   - Option C (scope note): the per-size values exist only for the model; the body maker still has to confirm the STEP per size (body.md:113). A short written confirmation from the maker is the closing step.
5. Your best reading: Option A with Option B on US 7 and US 13, because the per-size values are already in the project and the only open part is the maker's confirmation of the export.
6. Saved documents: none for this item (the cited STEP and drawing files are in the project, not in design/datasheets).

## Item 100
1. Item: 100, "Joystick centre press and feel: bench B6 (centre press) and B9 (feel, sealing, wear); cap feel and tilt in motion not tested."
2. Today:
   - B6 "Centre press by two opposite switches", bench, first housing print: design/architecture.md:398. This conflicts with the joystick text and the BOM: "A press on the centre closes SW2" (design/mfg/specs/joystick-nub.md:8) and "the centre press is the switch SW2 under the centre of the cap" (design/bom.csv:39, the Alps row). One centre switch, not two. Found by reading the three files against each other.
   - B9 is written twice: "Joystick at the bottom of the band (+150 degrees): feel when the hand grips an object, sealing of the 6.4 x 5.4 mm frame, wear" (architecture.md:511) and "Joystick on a curved shoulder: feel, sealing of the 5.0 mm opening, wear" (architecture.md:474). The current opening is 5.60 mm round (body.md:115, open point 9, "Closed in v7: the joystick opening is round, 5.60 diameter"), so architecture.md:474 is out of date.
   - The open items as the spec states them: "Bench items B6 (centre press) and B9 (feel, sealing, wear of the coating) can change this part." design/mfg/specs/joystick-nub.md:101.
   - "Cap feel, tilt clearance in motion (0.20 radial, static model), sealing of the round opening (B9), the DP420 bond on the coating: no bench." design/mech/thin/thin-notes.md:470.
   - Switch rating relied on: "The joystick opening relies on the switches' own rating (IP6X and IPX7) and the dam DAM1 for water" design/mfg/specs/joystick-nub.md:102.
3. Maker facts: (Alps Alpine SKTA tact switch with projection; saved as design/datasheets/w4_alps_sktaaae010_spec.pdf, 7 pages):
   - Operating force: "1.6 ± 0.5 N", the maximum load before the switch stops, applied at the projection centre (page 2, line 94).
   - Travel: "0.11 ±0.05 mm" (page 2, line 101).
   - Operating life: "300,000 cycles", with depression "2.1 N Max." (page 3, lines 222 to 226, item 9.1).
   - Protection: "IP6X equivalent" dust and "IPX7" water (page 3, lines 199 to 208, item 8.5).
   - The order code SKTAAAE010 (used in design/bom.csv) is not shown in this saved copy, nor in the two other saved Alps copies (slim_alps-skta-aaae010-orwin.txt and -p4-7.txt): a search for the code gave 0 hits. So no part code is given here (the code rule).
   - Feel of a cap on the switch: not in the sheet. Not found.
4. Options:
   - Option A (measurement step, B6, on the first housing print): press the cap centre with a force gauge (0 to 10 N, 0.1 N steps) at the centre and record the force at the first click and the travel with a dial indicator. Expected: each closure within the sheet's 1.1 to 2.1 N (1.6 ± 0.5 N, page 2 line 94) and travel 0.06 to 0.16 mm (0.11 ± 0.05, page 2 line 101). Outside: the switch or the cap seat is wrong; check the seat and the stem, then the switch. Cost: one print, a gauge; the press must not exceed 2.1 N on any switch (the life limit, page 3 line 224).
   - Option B (measurement step, B9, wear and sealing): on a printed or machined housing with the frame bonded in it (DP420 Black, joystick-nub.md:96, list item 2), run a press-and-release cycle with a fixture at 2.1 N maximum for 300,000 cycles only if the owner accepts a long bench run; a shorter 10,000-cycle run tests the start. Expected: no drop in contact (20 ohm max, page 3 line 222 onward) and no leak with the sealing water test (IPX7 equivalent). Outside: the cap or the frame fails; go to Option C. Cost: a fixture and a few weeks of bench time.
   - Option C (design change, not decided): a second centre switch or a stiffer cap, which changes the parts list. The lead decides.
   - Cap feel and tilt in motion: no maker value. Measure with the owner's hand on the first housing (the owner-confirmed feel) and record the result as the design target; no number is set here.
5. Your best reading: Option A now, to fix whether one centre switch closes at 1.6 ± 0.5 N (this also settles the B6 wording conflict), with Option B as the long wear test before the first lot.
6. Saved documents: design/datasheets/w4_alps_sktaaae010_spec.pdf (existing copy).

## Item 101
1. Item: 101, "Joystick opening relies on the switches' own ratings; still open."
2. Today:
   - "The joystick opening relies on the switches' own rating (IP6X and IPX7) and the dam DAM1 for water; dam material and the stiffener material are open item S26 (assembly.md section 5)." design/mfg/specs/joystick-nub.md:102.
   - The opening itself is a round 5.60 mm hole through the wall, with the cap CAP1 over it and the frame FRM1 bonded in it (design/mfg/specs/body.md, joystick opening row; joystick-nub.md:96 to 98).
   - The sealing of the round opening is B9 and is "not tested": design/mech/thin/thin-notes.md:470.
3. Maker facts: Alps SKTA data sheet (design/datasheets/w4_alps_sktaaae010_spec.pdf): "IP6X equivalent" dust and "IPX7" water, with the test steps at page 3, lines 199 to 208 (item 8.5). This rates the switch alone, not the opening with its cap and frame, so the sheet does not close item 101.
   - The IPX7 immersion depth and time (1 m, 30 minutes) come only from secondary web descriptions (one search; not saved, the standard text was not obtained): [not sourced] for use as a value.
4. Options:
   - Option A (measurement step, first housing): build the body with the cap, the frame and the dam; immerse the ring 1 m for 30 minutes (the IPX7 depth and time, [not sourced] until the standard text is checked); dry it; open it and check the switch contacts with a multimeter (20 ohm max, page 3, life-test table of the saved ALPS copy) and the inside for water with a paper towel. Expected reading: no water inside and no contact change. Outside: water inside; the seal is the fix (Option B). Cost: one housing and a tank.
   - Option B (fixed design value): a sealing ring of a named material round the frame or the cap, chosen with a supplier's data sheet; none is named in the files, so no part code is given here. Cost: one part and the dam material decision (S26).
   - Option C (no change): keep the switches' rating as the only seal, as the spec says now. This is the status quo, and the Alps copy does not prove it for the opening.
5. Your best reading: Option A on the first housing, because the switch rating is for the switch alone and the opening is a larger path; Option B only if the test shows water.
6. Saved documents: design/datasheets/w4_alps_sktaaae010_spec.pdf (existing copy).

## Item 102
1. Item: 102, "Mechanical dimensions marked ASSUMED: 30 lines in dimensions.csv (CHECKLIST says 25 rows); 32 lines in ring.py."
2. Today:
   - Counts from this run: `grep -c "ASSUMED" design/mech/dimensions.csv` gives 30 (the file has 155 lines); `grep -c "ASSUMED" design/mech/ring.py` gives 32. The checklist says "dimensions.csv from the table, ASSUMED marked (25 rows)" (design/mech/CHECKLIST.md:7).
   - Examples of the ASSUMED rows: min_wall 0.5 (design/mech/dimensions.csv:7), top_plate 1.0 (dimensions.csv:8), fold_w 8.0 "cable width; screen datasheet p.2 prints only the 4.8 mm tail length" (dimensions.csv:37), joy_stem_d 2.5 "stem drawing is an image only...; confirm from Alps drawing No.4" (dimensions.csv:49), fpc_conn_x, fpc_conn_y, fpc_conn_z 3.2, 5.2, 0.9 "FH35C-15S-0.3SHW 5.2 x 3.2 x 0.9" (dimensions.csv:106 to 108).
   - Conflict with item 48: fold_w is 8.0 mm (dimensions.csv:37), the screen cable is 12.4 mm wide at the fold (design/architecture.md:525), and the model folds 5.0 mm (design/architecture.md:757). Three widths in the files.
3. Maker facts:
   - Hirose FH35C-15S-0.3SHW(50) specification, saved as design/datasheets/w1_hirose_fh35c-15s-0.3shw50_spec.pdf: "THICKNESS OF FPC SHALL BE t=0.20mm" (text line 35 of the saved copy's text layer; the copy is partly unreadable).
   - The connector footprint 5.2 x 3.2 x 0.9 is not read from the saved drawing (design/datasheets/w1_hirose_fh35c-15s-0.3shw50_drawing.pdf, 7 pages): its text layer has no footprint dimension, and the image pages were not read in this run. Not found in text.
   - Joystick stem diameter: the saved Alps copy covers the switch, not the stem. Not found.
   - Printing service (PA12, min_wall): no maker document saved. Not found.
4. Options:
   - Option A (measurement step per row, one first article per part, 30 rows): measure the rows by group (printed parts, machined body, board, connector, switch) with calipers or a pin gauge on the sample. Expected reading: within the tolerance of the row's part or its maker sheet. Outside: change the row and the model. Cost: samples of each part and bench time.
   - Option B (fixed value, a reconciliation step first): make the rows of dimensions.csv and the lines of ring.py agree, one list with the source (maker file, owner's word, or assumption) for each row, and correct the checklist's "25 rows" to the real count. The count is fixed by the grep above: 30 in dimensions.csv and 32 in ring.py. This is an edit for the model owner.
   - Option C (the cable row first): set fold_w to the stock width (12.4 mm, see item 48) or to 5.0 mm once Tailor answers. This closes the widest conflict in the list.
5. Your best reading: Option B first (one list, one count), then Option C for the cable row, then Option A as the first-article measurement for the body rows.
6. Saved documents: design/datasheets/w1_hirose_fh35c-15s-0.3shw50_spec.pdf and design/datasheets/w1_hirose_fh35c-15s-0.3shw50_drawing.pdf (existing copies, not copied again).

## Item 103
1. Item: 103, "Mechanical values to confirm: mic port position, joystick stem diameter 2.5 mm, and availability of a non-metal M1.2 screw."
2. Today:
   - The list: "ASSUMED values to confirm: mic port position, joystick stem diameter 2.5, key and push plate, cable width, screw head 2.0 x 0.3, gasket depth 0.25, clear window 0.4, protection chip height, connector footprint, wire pad size, non-metal M1.2 screw availability." design/mech/mech-notes.md:70.
   - Mic port position: the microphone openings in the current model are the floor holes at X -11.770 and +11.770, Y -4.800 (design/mech/mic-path/mic-path.md:75); the older top-shell note has four openings at X -12.0, -5.5, +1.0, +7.5 (design/mech/mech-notes.md:6), which is out of date.
   - Joystick stem diameter 2.5 mm: "ASSUMED: stem drawing is an image only (parts/ui-pass2.md s4); confirm from Alps drawing No.4" (design/mech/dimensions.csv:49).
   - Non-metal M1.2 screw: "2 x M1.2 x 3 at (-12.35, 7.0) steel and (+12.35, 7.0) non-metal (PEEK or nylon, ASSUMED available), boss r1.0, head 2.0 x 0.3" (design/mech/mech-notes.md:33).
3. Maker facts:
   - Acoustic port of the microphone: "Acoustic Port (AP) Ø0.25 ±0.05" (design/datasheets/w1_knowles_spk0641ht4h-1_chipsmall.pdf, page 6, the package table, text line 348). The port position on the package is not given in the text layer; the mic-path uses the floor hole, not the package port.
   - Joystick stem: the saved Alps SKTA copy (design/datasheets/w4_alps_sktaaae010_spec.pdf) covers the switch, not the stem. Not found.
   - Non-metal M1.2 screw: one search returned a PEEK M1.2 pan head (pitch 0.25 mm, head Ø1.8 mm, head height 0.5 mm) and a PEEK M1.2 flat head (head Ø2.3 mm), both from a maker's catalog page (NBK). The maker PDF returned HTTP 403 to curl, so it is not saved. A search snippet is not an order code, so no code is given. Nylon M1.2: not found (the McMaster page excerpt has no M1.2 dimensions). The head sizes differ from the model's 2.0 x 0.3 head.
4. Options:
   - Option A (measurement step, first housing): mic port: measure the placed microphone's port on the board with a loupe and a rule, then compare its centre to X -11.770, Y -4.800 with a 0.2 mm tolerance. Expected: within 0.2 mm. Outside: move the hole in the body. Joystick stem: measure the stem on the first switch-and-cap sample with a pin gauge or a 2.5 mm drill shank. Expected: 2.5 mm within 0.05 mm. Screw: buy 10 PEEK M1.2 screws from the catalog (the lead orders) and check the head on a rule; expected: head within the 2.0 mm counterbore only if it is 2.0; the 1.8 head would need the counterbore changed.
   - Option B (fixed value, when a catalog code is saved): choose the PEEK M1.2 screw by its order code from a saved maker PDF (not yet saved), and change the counterbore to the head it shows. Until that PDF is saved, no code is fixed.
   - Option C (design change, not decided): use a steel screw in both places and a plastic boss elsewhere; the lead decides, since the non-metal screw was for the radio (antenna) path.
5. Your best reading: Option A for the mic port and the stem (each is a single caliper or gauge reading on a sample), and a catalog pull of the NBK PEEK M1.2 PDF before a screw is chosen, because its head is 1.8 mm against the model's 2.0 mm.
6. Saved documents: design/datasheets/w1_knowles_spk0641ht4h-1_chipsmall.pdf (existing copy, cited for the port). No new document saved: the NBK PDF returned 403 and was removed.

## Item 105
1. Item: 105, "Coating thickness (S29) is not known; no figure."
2. Today:
   - The bill-of-parts style row: "Coating (gloss black, PVD or DLC) ... no figure (thickness open, S29)." design/architecture.md:881.
   - S29: "Body finish and material (17.29): which gloss black coating on titanium (PVD or DLC), its thickness, gloss and wear on a ring; and whether a black ceramic body is makeable..." design/architecture.md:527.
   - Body spec: "Coating thickness, roughness, masking at the glass seat and the microphone seats: the maker answers." design/mfg/specs/body.md, open point 4 (the Open points list).
   - The coating adds to every face. The joystick frame bond gap is 0.10 mm radial (design/mfg/specs/body.md, joystick frame row; joystick-nub.md, list item 2 at line 96), so a coating on the frame and the opening both reduce that gap.
3. Maker facts:
   - One web search (black PVD or DLC on titanium, thickness) returned retailer and blog pages only; the figures in them (0.3 to 5 micron ranges) are not maker data, so they are not saved and are not used as a value. Not found: a coater's datasheet with a thickness for gloss black on Ti-6Al-4V. The search also said the thickness is generally only known from the maker.
4. Options:
   - Option A (measurement step, first coated sample, no maker needed to start): have the coater coat a flat Ti-6Al-4V coupon in the same batch, and measure the coating by a ball-crater (calotest) section or a cross-section under a microscope; a stylus step on a masked edge is the quick check. Expected reading: a single value per face, reported with its method. Outside the frame gap (0.10 mm radial minus both faces' coating): the frame or the opening must change. Cost: one coupon and the coater's test.
   - Option B (fixed value, from the coater): the coater writes the coating thickness per face in its quote. Not yet asked; the lead or owner sends the request. No value is fixed here.
   - Option C (change of process): DLC instead of PVD, a different thickness class; the lead decides, since the owner chose gloss black.
5. Your best reading: Option B as the written request, with Option A as the coupon test in the same batch, because the coater's own number is the only maker fact that closes this item and the test confirms it.
6. Saved documents: none for this item.

## Item 106
1. Item: 106, "DP420 bond on the gloss black coating is not tested."
2. Today:
   - "The DP420 bond on the gloss black coating is not tested" design/mfg/assembly/v7-update-notes.md:28; "the DP420 bond on the coated titanium" design/ecad/ring/v7-wiring-notes.md:64 (the bench item is B9, same line).
   - The frame FRM1 is bonded in the opening with 3M Scotch-Weld DP420 Black, 0.10 mm radial gap (design/mfg/specs/body.md, joystick frame row; design/mfg/specs/joystick-nub.md, list item 2 at line 96). The body and the frame are coated gloss black in the same batch (body.md, Material section; joystick-nub.md:97, list item 3).
3. Maker facts: (3M Scotch-Weld DP420 Black TDS, saved as design/datasheets/w11v_3m-dp420-tds.pdf; copy from a third-party host, see item 45):
   - The metals table (page 4, saved text lines 196 to 210) lists aluminium, cold rolled steel, copper, brass, stainless steel and galvanized steel, with the surface preparation used for each (for example stainless steel, "MEK/abrade/MEK", 1800 psi, DP420 Black). Titanium is not in the table (searched the saved text for "titan": no hit). Not found: a bond value on titanium, or on any coated metal.
   - Surface preparation: the saved text gives "E. Isopropyl Alcohol/Abrade/Isopropyl Alcohol Surface Preparation" (text line 418 to 420). A coating layer is not discussed in the sheet. Not found.
   - The sheet's values are "representative or typical only and should not be used for specification purposes" (page 1, text line 33 to 34).
4. Options:
   - Option A (measurement step, coupon, first): make 5 lap-shear coupons of Ti-6Al-4V with the same gloss black coating from the batch, abrade or not as the process plan says, bond with DP420 Black mixed 2:1 by volume (the TDS page 1, line 53), cure as the sheet's cure table says (page 3, lines 127 to 138; the cure for the frame is the lead's choice), then pull them in a tensile test and record the load and the failure mode. Expected reading: cohesive failure in the adhesive at or above the stainless-steel value in the sheet, 1800 psi (page 4 line 209) as a floor [ESTIMATE, not a Ti value]. Outside: adhesion failure at the coating (a clean break at the coating) means the coating is not bondable; go to Option C. Cost: 5 coupons and a pull tester.
   - Option B (fixed value, process): an abrade-then-clean step on the coated frame seat, as in the TDS's section E (text line 418), so the fixed step is known before the coupon test. This is a process choice, not a measured value.
   - Option C (design change, not decided): add a mechanical lock (a groove or a shoulder) on the frame so it does not depend only on the adhesive; the lead decides, since the frame's geometry is fixed in v7.
5. Your best reading: Option A on five coupons with the coating from the batch, because the sheet has no titanium or coated-surface value; Option C only if the coupons fail at the coating.
6. Saved documents: design/datasheets/w11v_3m-dp420-tds.pdf (text copy in the scratchpad folder w11v).

## Item 107
1. Item: 107, "Ring weight is not known: most parts have no figure; the cover glass has no density or mass source (S5)."
2. Today:
   - "Stated masses of the ring: the motor, 0.32 g (0.288 to 0.352 g). Every other line: no figure. Result: the weight of the ring is not known, and S5 (under 12 g) can be neither confirmed nor refused from these files. What closes it: a density per material from the body maker, the glass maker and the li..." design/architecture.md:883.
   - "This sum is a lower bound of the ring's weight. Not in it, because no source gives a density or a mass: the cover glass (332.87 mm3, glass grade not chosen), the cell (303.6 to 419.6 mm3 across US 7 to 13, custom, no mass from its maker), the band liner (84.4 to 106.4 mm3, resin not chosen), the scr..." design/architecture.md:906.
   - The S5 target is "under 12 g" (design/architecture.md:883).
   - The weight estimate is computed by design/mech/mass.py (volumes times the densities in its DENS table, lines 11 to 23); its output is out/mass-estimate.csv (design/mech/mech-notes.md:58).
3. Maker facts:
   - Cover glass density: Corning's Gorilla Glass 3 product sheet gives 2.39 g/cm3 in the search results. The sheet itself could not be saved: curl returned HTTP 403 from corning.com, and a third-party copy returned 403 too. So the figure is [not sourced] until the sheet is saved. The cover glass grade is open (item 109), so this density also needs the glass grade.
   - Cell, band liner resin, screen module, switch, microphone: no maker mass or density in the saved documents for the parts as chosen (the cell is custom; the resin is not chosen). Not found.
4. Options:
   - Option A (measurement step, first article): weigh each part on a 0.01 g balance: the glass, the cell, the board with parts, the body, the cap and frame, the liner (cast), the screen module, and the motor (the motor is 0.32 g per architecture.md:883). Add them. Expected: the sum within 10 percent of the mass.py estimate, which is a lower bound (architecture.md:906). Outside: the density or the volume is wrong for that part; fix its row. Cost: one balance; the parts exist only after the first article.
   - Option B (fixed density for the glass, then recompute): set the glass density to 2.39 g/cm3 once the Corning sheet is saved, and recompute the glass mass from the 332.87 mm3 volume (architecture.md:906): 0.796 g (CALC). This closes the glass row only.
   - Option C (keep the weight open): report the sum as a lower bound and state S5 cannot be confirmed; this is the status quo.
5. Your best reading: Option A on the first article for the whole sum, with Option B now as the one row that has a maker density; the lead then decides on S5.
6. Saved documents: none saved for this item (the Corning sheet did not download).

## Item 108
1. Item: 108, "Densities in the weight estimate are ASSUMED or unverified (cell, silicon packages, screen, foam, mic, switch, clear parts)."
2. Today:
   - Density table with the source of each value: design/mech/mass.py:11 to 23. Lines 15 (cell 2.0, "ASSUMED: Li-polymer pouch about 2 g/cm3 overall; replace with the Grepow sample weight"), 16 (silicon packages 2.3, ASSUMED), 17 (screen 2.5, ASSUMED: "AMOLED module mostly glass"), 20 (foam 0.3, ASSUMED: foam pad), 21 (mic 2.0, ASSUMED), 22 (switch 2.0, ASSUMED), 23 (clear parts 1.2, ASSUMED). Lines 12 to 14 (PA12 1.01, glass 2.42, FR-4 1.85) and 18 to 19 (steel 7.9, silicone 1.1) are marked "handbook, unverified" (mass.py:10: "None of these was fetched in this run").
3. Maker facts: (saved documents):
   - Foam: Rogers PORON 4701-40 Soft (copy hosted by Mueller-Ahlhorn, design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf), page 2, line 55: density "240 (15), 320 (20), 480 (30)" in kg/m3 (lb/ft3) by density group, ASTM D3574 Test A. So the foam is 0.24 to 0.48 g/cm3, and the 0.3 in mass.py:20 falls inside that range. The foam type in the ring is not this family (item 74), so this is the family's range, not the chosen part's.
   - Silicone: Smooth-On Dragon Skin NV bulletin (design/datasheets/w11v_smoothon-dragonskin-series-tb.pdf), page 1, saved text line 58: Dragon Skin 10 NV, specific gravity "1.07" (mixed). The mass.py silicone value 1.1 (line 19) is close; the 1.07 is a maker value for a silicone not chosen for the ring.
   - Epoxy DP420 (for the frame and the dam, not in mass.py): base 9.3 to 9.7 lb per gallon (design/datasheets/w11v_3m-dp420-tds.pdf, page 1, lines 50 to 51), which is about 1.11 to 1.16 g/cm3 (CALC).
   - Glass: 2.39 g/cm3 in Corning's Gorilla Glass 3 sheet, found in a search result only (not saved, not opened; see item 107). Not verified.
   - Cell, silicon packages, screen, mic, switch, clear parts, PA12, FR-4, steel: no saved maker density. Not found in the saved documents (the Knowles and Alps copies give no weight; not searched further in this run).
4. Options:
   - Option A (measurement step, first article per material): weigh 10 pieces of each material (foam, clear adhesive, mic, switch, cell) on a 0.1 mg balance and divide by the volume, or weigh the part and divide by its CAD volume. Expected: the density within 10 percent of the mass.py value. Outside: change the DENS row, with the measured number and the sample count written in the row's source column.
   - Option B (fixed value from a saved maker sheet): foam 0.3 is supported by the PORON range (page 2, line 55), so it can change its source text now without a measurement, and silicone 1.07 (Dragon Skin page 1, line 58) can replace 1.1 for the silicone row. Cost: text edits in mass.py only; no part is chosen by this.
   - Option C (keep ASSUMED): leave the rows, and state in the weight result that these are estimates; this is the status quo.
5. Your best reading: Option B for foam and silicone now (both have a saved sheet), and Option A for the cell, the mic and the switch on the first article, since no saved maker document gives their density.
6. Saved documents: design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf; design/datasheets/w11v_smoothon-dragonskin-series-tb.pdf; design/datasheets/w11v_3m-dp420-tds.pdf.

## Item 109
1. Item: 109, "Cover glass grade and forming are defaults to confirm with the maker; dimensions refer to open point 2."
2. Today:
   - Material: "Default, to confirm with the maker: chemically strengthened aluminosilicate glass... Brand, grade and the strengthening depth and surface stress: open point 1." design/mfg/specs/cover-glass.md:12.
   - Forming: "Default, to confirm with the maker: formed (hot-bent) to the arc and rolls, then chemically strengthened, then printed. Whether one can form an arc of 30.7 mm with 1.0 mm and 1.2 mm rolls at 1.10 m..." design/mfg/specs/cover-glass.md:15.
   - Dimensions that refer to open point 2: "glass thickness at the centre | 1.10 mm | open point 2" (cover-glass.md:28); "glass thickness over the screen edge | 0.42 mm | open point 2" (cover-glass.md:29); "face arc radius | 30.7 mm | open point 2" (cover-glass.md:30); the glass plan outline "29.2958 x 14.429 mm" (cover-glass.md:44, marked open point 2).
   - Open point 2 in the cover-glass spec is the glass thickness and the outline together; it is not a separate value in the file.
3. Maker facts:
   - Corning Gorilla Glass 3 product sheet (search snippet only): density 2.39 g/cm3 and the grade family. The sheet could not be saved: corning.com returned HTTP 403 to curl (twice) and a third-party copy returned 403. Not opened in this run, so no thickness or forming limit is quoted from it. Not found in any saved document: a thickness or radius limit for chemically strengthened aluminosilicate at 1.10 mm with a 30.7 mm arc.
   - The sheet's density is for the grade, not a value the spec states; the grade is open (item 107).
4. Options:
   - Option A (fixed value from the glass maker, a written answer): ask the glass maker (through the lead, not this helper) for the grade, its thickness range at 1.10 mm and the minimum hot-bend radius at 30.7 mm; the answer closes "defaults". Cost: a quote and an engineering round.
   - Option B (measurement step, on sample glass when a sample exists): read the thickness with a micrometer at 5 points on the centre line (expected 1.10 mm within the tolerance the maker gives; the spec has none yet) and the radius of the formed sample with a radius gauge (expected 30.7 mm). Outside: change the arc or the thickness and the lead decides. Cost: one formed sample.
   - Option C (fixed start value): keep 1.10 mm, 30.7 mm and aluminosilicate as the start values, since they are the design's and the forming note is the only doubt. This is the status quo.
5. Your best reading: Option A with Option B on the first formed sample, because the forming limit is the maker's answer and no saved document gives it.
6. Saved documents: none (the Corning sheet did not download).

## Item 110
1. Item: 110, "Glass seal ring SEAL1 is 0.05 mm thick but its tape and sealing are not settled; the glass seat has no room for one (K-A4)."
2. Today:
   - "glass seal ring SEAL1 | 0.05 mm thick | open | perimeter ring between the glass underside and the body seat, Z 2.70 to 2.75; the seat is lowered 0.05 mm in the body; the glass and the outer shape do not change" design/mfg/specs/cover-glass.md:43.
   - K-A4: "No glass-to-body adhesive or seal existed, and the seat had no room for one." design/mfg/assembly/assembly.md:321; its proposal: "lower the glass seat by the seal's th..." (the same row).
   - The assembly step for the seal lists it as open: "Glass seal SEAL1: the tape and its compressed thickness (the seat depth is set, 0.05 mm) | 23 | the mechanical designer, with the glass maker | S26" design/mfg/assembly/assembly.md:360 (the row is at line 360).
   - The body seat is lowered 0.05 mm for it: design/mfg/specs/body.md:82 (the row "glass seat lowering | 0.05 mm").
   - The claim "no water or dust rating" for the ring: design/mfg/assembly/assembly.md:347.
3. Maker facts:
   - One web search for 0.05 mm double-coated tape (3M) gave 0.05 mm polyester-carrier tapes (55256; 9731-050, a clear PET tape with an acrylic face and silicone back) and a 0.8 mm polyethylene foam tape (9508W). These are search snippets; none was opened or saved. A 0.05 mm film tape is an adhesive, not a compressible seal, so none of them is a seal for a 0.05 mm gap. Not found: a compressible 0.05 mm seal (foam or silicone) with a data sheet.
   - The PORON 4701 sheet (design/datasheets/w11v_poron-4701-40-soft-datasheet.pdf) starts at 0.79 mm thickness (page 2, lines 57 to 58), so it is not a 0.05 mm seal either.
4. Options:
   - Option A (fixed design value, a seal type): a 0.05 mm seal cannot be a foam at the sheets seen; the choice is either a 0.05 mm PSA film (adhesive only, no seal under compression) or a glued seal ring with a stated compression. The first option needs a sealing test; the second needs a sheet. Neither code is given here.
   - Option B (measurement step, first body and glass): dry-fit the glass on a bead of the chosen sealant or film, with the seat lowered 0.05 mm; measure the gap with a feeler gauge at 4 points (expected 0.00 to 0.05 mm, with the film or seal in place); then a water-spray test at IPX-style conditions (the rating is open; the test result is the first evidence). Outside: the seat depth or the seal thickness changes; the lead decides.
   - Option C (design change, not decided): give the seal more room by lowering the seat more, or by a glass-to-body adhesive with no separate seal; the lead decides, since the seat depth is a body value (body.md:82, glass seat row).
5. Your best reading: Option B on the first body, because no saved document gives a 0.05 mm compressible seal; Option A's film is the quickest test of whether any seal is needed.
6. Saved documents: none new; the PORON copy is cited above.

## Item 99
1. Item: 99, "Body defaults: CNC from bar with multi-axis, titanium grade and black PVD, ISO 2768-m; each to confirm with the maker."
2. Today:
   - Material: "Titanium grade 5 (Ti-6Al-4V), machined from bar (architecture 17.29)." design/mfg/specs/body.md:14.
   - Process: "Default, to confirm with the maker: CNC machining from bar (multi-axis), one piece." design/mfg/specs/body.md:17.
   - Finish: "one dark glossy finish... coated gloss black (PVD or DLC; the maker names the process)." design/mfg/specs/body.md:20 (the "Finish and colour" section).
   - General tolerance: "General: ISO 2768-m (default, to confirm with the maker)." design/mfg/specs/body.md:23.
   - The model's own default: "Ti-6Al-4V grade 5, black PVD (default, to confirm with the maker" design/mfg/tools/draw_merged32c.py:35.
   - Open point 1 is who machines the one-piece body and whether it can be one piece (body.md, Open points list, item 1).
3. Maker facts: (Ti-6Al-4V grade 5 supplier data sheet, Smith Metal, saved as design/datasheets/w11v_smith-ti-6al-4v-grade5-datasheet.pdf, fetched from https://www.smithmetal.com/pdf/titanium/ti-6al-4v-grade-5.pdf, one page):
   - Chemistry, "Bar to ASTM B348 Grade 5": aluminium 5.5 to 6.75 percent, vanadium 3.5 to 4.5 percent, iron max 0.40, oxygen max 0.20, carbon max 0.08, nitrogen max 0.05, hydrogen max 0.015 (page 1, the "Chemical Composition" table; the saved text has the rows at lines 35 to 38).
   - Mechanical, minimum: UTS 895 MPa, 0.2 percent proof 828 MPa, elongation 10 percent in 4D, reduction of area 25 percent (page 1, "Mechanical Properties" rows, saved text lines 41 to 46). Typical: UTS 1000 MPa, proof 910 MPa, elongation 18 percent, modulus 114 GPa.
   - The sheet names ASTM B348 Grade 5, UNS R56400 (saved text line 23). The sheet does not give a machining, a coating or an ISO 2768 class; those are not in the data sheet. Not found: a machining method statement from a maker.
   - Coating: the black PVD is not a titanium property; no coater document is saved (see item 105). Not found.
   - ISO 2768-m: a general tolerance standard; no saved copy. Not checked here: [not sourced].
4. Options:
   - Option A (fixed value, the grade): keep Ti-6Al-4V grade 5 to ASTM B348 as the value, with the minimums above as the acceptance numbers the body maker must meet on the bar certificate. Cost: none beyond the certificate.
   - Option B (measurement step, first article): ask for the mill certificate with the first bar; read the chemistry and the 0.2 percent proof on the certificate and compare to the minimums above; expected: within the minimums. Outside: reject the bar. Cost: a certificate line.
   - Option C (machining route, the maker's answer): the one-piece machining question (body open point 1) is the maker's; no value is fixed here. The lead chooses between one piece and the joined parts after the maker's quote.
   - ISO 2768-m: keep as the default (body.md:23); the first-article check is the same as in item 97.
5. Your best reading: Option A with Option B on the first bar (the certificate is the cheapest check), because the grade and its minimums are in a saved sheet and only the one-piece machining route is open.
6. Saved documents: design/datasheets/w11v_smith-ti-6al-4v-grade5-datasheet.pdf

## Item 160
1. Item: 160, "Model and file revisions still to follow: exterior variant merged32h, inside model v5 and v7 not built, wiring diagram, parts list; record-cap.md has no v7 content; exterior files hold a light solid."
2. Today: (each statement checked against the files as they are now)
   - "Files that follow at the next revisions: the exterior (variant merged32f), the inside model v5, the wiring diagram and the parts list (8 pins per microphone in place of 5)..." design/architecture.md:661. The variant name is stale: the exterior is merged32h, with its report at design/look/s1/merged32h-report.md (the file exists).
   - "To follow: exterior variant merged32h (seven sizes, metal round the opening measured), then the inside model..." design/architecture.md:827. The seven-size exterior exists (design/look/s1/merged32h-report.md, and the STEP files design/look/s1/out/ring-merged32h-us9.step, dated 12 Nov).
   - "The inside model v7 is not built yet." design/mfg/assembly/v7-update-notes.md:29. Stale: design/mfg/parts/index.csv line 2 reads "design/mech/thin/thin.py v7 built at US 9", and design/mfg/parts/export_parts_v7.py exists. The body STEP files of v7 are dated 11 Nov (design/mfg/parts/body/body-us9.step).
   - "Exterior files still hold a `light` solid." design/supplier-package/v3-notes.md:66. Checked: `grep -c -i light design/look/s1/out/ring-merged32h-us9.step` returns 0 (the file is dated 12 Nov). The statement is stale for that file.
   - "design/mfg/specs/record-cap.md has no v7 content" design/supplier-package/v3-notes.md:69. Checked: `grep -c v7 design/mfg/specs/record-cap.md` returns 0. True.
   - Wiring diagram and parts list: the parts list exists as design/bom.csv; the schematic is design/ecad/ring/ring_band.kicad_sch with the netlist design/ecad/ring/netlist.csv. Whether the wiring diagram "to follow" is this schematic: not decided by the files read.
   - The "8 pins per microphone in place of 5" is in architecture.md:661; not checked against the board files in this run.
3. Maker facts: none. This is a revision-status item; no maker document applies. Not applicable.
4. Options:
   - Option A (fixed value, the status list): replace the five statements with the checked state above, one line each with its file and date. This is a text edit for the spec owners; the revision names (merged32h, v7) are the fixed values.
   - Option B (measurement step, per file): for each named file, run the check the statement names (the grep counts above, the STEP listing for the light solid, the existence of each revision file) and record the output in the file's status line. Expected: each statement either matches its check or is marked stale. Cost: minutes, no bench.
   - Option C (keep as is): leave the list open; the lead then reads five stale claims as open work. This is not recommended.
5. Your best reading: Option B followed by Option A, because four of the five statements are stale or confirmed by a single check each, and the fixed values are already in the files.
6. Saved documents: none for this item.

## questions_for_owner
1. Is a stock Tailor Pixels TOH095XVT-01 module on hand to measure the tail width and the bend (item 48, option A)? Evidence: no sample is named in design/architecture.md:757 or in any file read.
2. Who sends the 5.0 mm cable question to Tailor Pixels (item 48, option B), and who sends the moulder question on the 0.79 mm LCP wall (item 85)? Evidence: design/architecture.md:525 and design/case/c5d-open-points-handover.md:44 name the suppliers but no sender; this helper does not write to any supplier.
3. Is the recording light fully removed, so that S25 can close? Evidence: design/architecture.md:523 says "CLOSED by 17.30"; design/architecture.md:698 still says "Open item S25"; design/mech/light-path/light-path.md:117 still lists S-L1.
4. Is the joystick centre press one switch (SW2) or two opposite switches? Evidence: design/bom.csv:39 and design/mfg/specs/joystick-nub.md:8 (one switch, SW2); design/architecture.md:398 (B6, "two opposite switches").
5. Is the 0.10 mm membrane limit a requirement from you or a default? Evidence: design/architecture.md:58 gives "at most 0.10 thick" with "no part chosen"; the only saved Gore vent is 0.24 mm (design/datasheets/w11v_gore-acoustic-vents-gaw111-gaw112-datasheet.pdf, page 5 line 148).
6. Which water rating is the requirement for the ring (IPX7 equivalent, or none yet)? Evidence: design/mfg/assembly/assembly.md:347 says "no water or dust rating" can be claimed; design/mfg/specs/joystick-nub.md:102 relies on the switches' rating.
7. Is the ring weight target "under 12 g" (S5) a hard requirement? Evidence: design/architecture.md:883 says the weight cannot be confirmed or refused from the files.

RESULT: done, all 25 W11 items have a block with the six fields; items 48, 85, 53, 110, 36 and 73 each depend on a maker or owner answer that no saved document gives, and are marked so in their fields.
