# Version C2 arithmetic: ring stores 464.4 MB per recorded hour including block headers (lead, 2026-11-10).
mb = 464.4
fs_raw = 1.5
fs_bulk = 19 * 64 * 1000 / 1e6
hs = 2.0
print(f"raw 12 Mbit/s: {mb} / {fs_raw} = {mb/fs_raw:.1f} s = {mb/fs_raw/60:.2f} min (bound)")
print(f"bulk ceiling {fs_bulk:.3f} MB/s: {mb} / {fs_bulk:.3f} = {mb/fs_bulk:.1f} s = {mb/fs_bulk/60:.2f} min per recorded hour")
print(f"10-hour day {10*mb/fs_bulk/60:.1f} min; 17-hour ring {17*mb/fs_bulk/60:.1f} min")
print(f"hours copied in 90 min: {90*60*fs_bulk/mb:.2f} h")
print(f"high speed limited by 2 MB/s: {mb/hs:.1f} s = {mb/hs/60:.2f} min; difference {(mb/fs_bulk-mb/hs)/60:.2f} min")
print(f"TPS63802 R1 511 k, R2 91 k: VOUT = 0.5 x (1 + 511/91) = {0.5*(1+511/91):.3f} V")
print(f"TPS63802 R1 560 k, R2 100 k (C1): VOUT = {0.5*(1+560/100):.3f} V")
