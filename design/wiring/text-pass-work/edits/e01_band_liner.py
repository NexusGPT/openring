D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/specs/band-liner.md"
L56="lead-decisions.md row 'liner resin (item 36, material)' 2026-11-13 04:15"
L38="lead-decisions.md row 'item 36' 2026-11-13 03:56"
L39="lead-decisions.md row 'item 45' 2026-11-13 03:56"
EDITS=[
(F,"(the maker files are exported from the inside model v7)","(the maker files are exported from the inside model v9)","model v9 (model-v9-notes.md section k)"),
(F,"A 0.3 mm skin of skin-safe resin that closes","A 0.3 mm skin of resin (Master Bond EP30Med) that closes",L56),
("%s"%F,"Default, to confirm with the maker: a skin-safe cast resin. The resin grade is open: the maker proposes one with its skin-contact certificate (open point 1).",
 "Master Bond EP30Med: two parts, low viscosity, cures at room temperature, stated by its maker to meet ISO 10993-5 and USP Class VI (maker's guide, page 12). ISO 10993-5 is a cell-toxicity test, not a skin-wear test: no skin claim is made for version 1. Its viscosity and cure time are only in a sheet that could not be downloaded: the test strip of item 36 shows whether it fills 0.075 mm, and the cell's temperature is measured during the first cure (limit 45 degrees C).",L56),
(F,"The cell is live during the cure and must not exceed its limit: Grepow answers the limit (K-A8). Whether the ribbons can float 0.075 mm inside a single cast, or the liner must be made as a laminate first, is open (K-A5, S19, B8). Repair after casting is not possible (B8).",
 "The cell is live during the cure and must not exceed 45 degrees C (specs/cell.md, Requirements on the cell; K-A8). Whether the ribbons can float 0.075 mm inside a single cast, or the liner must be made as a laminate first, is open (K-A5, S19, B8); the liner keeps 0.3 mm with 0.075 mm of resin on each side of a circuit, and before the first ring the builder casts one test strip (60 mm of the circuit stack in a 0.3 mm skin), cuts it and reads the resin on each face with a 10x loupe: at least 0.075 mm on each side and no void over copper (item 36). Repair after casting is not possible: a ring with a damaged liner is scrapped (B8, item 36).",L38),
(F,"1. Resin grade, supplier, skin-contact certificate: the maker proposes.","1. Resin: Master Bond EP30Med (decided). Its skin-contact claim: none for version 1 (ISO 10993-5 is a cell-toxicity test). Viscosity and cure time: not in a saved sheet; the test strip of item 36 shows.",L56),
(F,"3. Cure temperature and time, and what the cell and flex tails tolerate: the maker with Grepow.","3. Cure temperature and time, and what the flex tails tolerate: the maker. The cell never goes above 45 degrees C (specs/cell.md); the first cure measures it.",L56),
(F,"The slot seal (with the motor window seal SEAL2 on US 7 to 9) and the dam DAM1 of the joystick pocket come BEFORE the cast (design/mfg/assembly/assembly.md steps 19 and 20; the sealant and the dam material are not chosen, open item S26).",
 "The slot seal (with the motor window seal SEAL2 on US 7 to 9) and the dam DAM1 of the joystick pocket come BEFORE the cast (design/mfg/assembly/assembly.md steps 19 and 20); the sealant of the slots and of SEAL2 is 3M Scotch-Weld DP420 Black (item 45); the dam material is not chosen (open item S26).",L39),
(F,"sealed from the channel side before the cast (step 19); inside model v8","sealed from the channel side with 3M Scotch-Weld DP420 Black before the cast (step 19; item 45); inside model v8",L39),
(F,"US 7, 8 and 9 only; same sealant and same step as the floor slots, before the cast (17.27)","US 7, 8 and 9 only; same sealant (3M Scotch-Weld DP420 Black, 0.80 cubic mm per window, item 45) and same step as the floor slots, before the cast (17.27)",L39),
]
