D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"architecture.md"
LD="lead-decisions.md row "
EDITS=[
(F,"Two capacitors of 10 uF, C83 at the input and C84 at the output; C84 is also","Two capacitors, C83 of 10 uF at the input and C84 at the output (C84 is 4.7 uF since the circuit simulation, Murata GRM155R61A475MEAAD, 10 V, 0402; it was 10 uF); C84 is also",LD+"'sim finding 4 (item 41)' 2026-11-13 01:23 and 'sim finding 4, correction' 02:07"),
(F,"| 12.6 | Microphone membrane cut to size | Gore | GAW112 die-cut, 1.6 mm outer, 0.8 mm inner, adhesive ring |","| 12.6 | Microphone membrane cut to size | Gore | GAW112 die-cut, 1.6 mm outer, 0.8 mm inner, adhesive ring (superseded 2026-11-13: Saati Acoustex 010a mesh disc on a ring of tesa 61305, cut by the builder with punches of 2.0 and 1.0 mm, item 73; no Gore part) |",LD+"'item 73' 2026-11-13 04:15"),
(F,"(no density, materials not chosen)","(no density in the files; since 2026-11-13 the materials are named: ADH1 tesa 69404, FOAM1 Nitto SCF AN010, SEAL1 tesa 61305, SEAL2 3M Scotch-Weld DP420 Black, gaskets Nitto SCF, membranes Saati Acoustex 010a on tesa 61305)",LD+"'items 45, 73, 74, 96 rest, 110'"),
]
