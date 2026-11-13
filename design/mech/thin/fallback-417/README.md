# fallback-417: inside model v10 (4.17 mm block, stock screen), kept as the fallback

What it is: the ring's inside model v10 for the 4.17 mm block with flat glass and the stock screen TOH095XVT-01 in layout C (cable folded at the fingertip end into J1 on the board's screen face), on the exterior ring-merged417flatw-us<N>.step, the routed board (placement-final.csv), side slits with their seal SEAL3, dam DAM1 option A. Since the owner chose the custom panel and the 3.20 mm block (13 Nov 2026), it is not the target; it is the fallback if the stock screen comes back.

State (from ../model-v10-notes.md and ../out/v10/):
- US 9 built and checked with these files: `RESULT FAIL pairs=1652 parts=58`, exit 1 (../out/v10/final_us9.log), only the three findings of the -Y side slit against the motor pocket (rim 0.000 against 0.40, window 0.1210 against 0.30, twice). The owner chose "Sealed opening" for it; the model does not have that opening yet.
- US 7 (`RESULT FAIL pairs=1652 parts=58`, 2 findings, window 0.2454) and US 8 (3 findings, rim 0.000, window 0.1416) also ran (../out/v10/final_us7.log, final_us8.log). US 10 to 13: not finished (runs stopped on the lead's word, ../out/v10/final/par_stopped.log).
- placement.csv, layers.json and us9/ are the US 9 outputs of 18:23 (copied from ../out/v10/sizes/us9/).

Files and sha256:
```
94cca5615fae7f132e67d928bb5337a8f63509e6f2d92f6a664e38546a216105  thin.py
2c793056c2b8f931fbb0c80e6e4859e720b9e52d0b62a6ab0dd07edbaa91f02c  check_thin.py
d8b2a1e0c7081ea691d30fcce563526cccdfac642cac37dfb0a404f5b868acbf  placement.csv
45fafd2fae1f69119b10d89840bbcb5395dcbad618d80437fb73bfe6a0abc127  layers.json
bc129a6c7417ba9d867643ade9dc2b88e50a2341a221dd1a603d34792bdbe184  thin-notes-v10-section.md
c3b532053a78ca2c614eeb48755099f6247f4628815fbf6b1d4ecc8a7315e7cd  us9/thin-inside.glb
2d4bc07132b71fc3d863830cd30e31ac4a1f46bafe82a2432a19ec0ef5839048  us9/thin-inside.step
bbeb560e51de413a8a6a90da8e8e41ee781f481a1aaffd1c2ec18d2554c2d541  us9/triangles.txt
```
(thin.py sha1 8eff4bf8..., check_thin.py sha1 2cf73958..., the hashes the notes cite.)

How to run it from this folder (writes placement.csv, layers.json and out/ here; the exterior is read from design/look/s1/out):
```
cd design/mech/thin/fallback-417 && THIN_EXTERIOR=design/look/s1/out/ring-merged417flatw-us9.step THIN_OVERRIDE="bore_d=18.9452" nice -n 19 design/.venv/bin/python thin.py
cd design/mech/thin/fallback-417 && THIN_EXTERIOR=design/look/s1/out/ring-merged417flatw-us9.step THIN_OVERRIDE="bore_d=18.9452" nice -n 19 design/.venv/bin/python check_thin.py
```
Other sizes: the bore from design/look/s1/out/sizes.csv and the file ring-merged417flatw-us<N>.step. The check builds the model itself and reads out/thin-inside.glb, placement.csv and out/triangles.txt of this folder, so build first. One size takes about 45 to 60 minutes under load, about 4 GB of memory.

Notes: model-v10-notes.md (copy of ../model-v10-notes.md at the end of the work), thin-notes-v10-section.md (the "Model v10" section that was in ../thin-notes.md; that file is back to v9).
