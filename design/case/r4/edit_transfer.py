"""Transfer figures of case-architecture.md section 1 follow design/firmware.md line 718 (234.0 MB per recorded hour, 192.4 s = 3.21 min) and the cell
hours of requirements.md row P2 (4.3 to 7.8 hours by ring size). Arithmetic done here and printed; each replacement must match once."""
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case-architecture.md")
MB = 234.0
fs = MB / 1.216
f = dict(line=MB / 1.5, bulk_s=fs, bulk_min=fs / 60, day=10 * fs / 60, p4_s=MB / 2.0)
f["p4_min"] = f["p4_s"] / 60
lo, hi = 4.3 * round(f["bulk_min"], 2), 7.8 * round(f["bulk_min"], 2)
print("line rate %.1f s = %.2f min; bulk %.1f s = %.2f min; 10 h %.1f min; P4 %.1f s = %.2f min, gain %.2f; 4.3 h %.1f min, 7.8 h %.1f min; per 60 min %.1f h"
      % (f["line"], f["line"] / 60, fs, fs / 60, f["day"], f["p4_s"], f["p4_min"], round(fs / 60, 2) - round(f["p4_min"], 2), lo, hi, 60 / round(fs / 60, 2)))
s = open(P, encoding="utf-8").read()
R = [
    ("C3 keeps that header ratio (assumption, LIST): 230.4 x 1.0078 = **232.2 MB per recorded hour** [CALC].",
     "Stored bytes (r4, following `design/firmware.md` line 718): 3,600 s / 0.512 s = 7,031.25 chunks x 33,280 bytes = **234.0 MB per recorded hour** [CALC] (C3 had 232.2 MB from the old header ratio)."),
    ("232.2 / 1.500 = 154.8 s = **2.58 min**.", "234.0 / 1.500 = 156.0 s = **2.60 min**."),
    ("232.2 / 1.216 = 190.96 s = **3.18 min per recorded hour. This is the planning figure for the chosen part.** A 10-hour day: 31.8 min. A full ring by storage (4 GB, 4,000 / 232.2 = 17.2 hours): 54.8 min. The ring's cell limits recording to 3.8 to 5.0 hours at 4.0 mA (A5-draft 17.10): 3.8 x 3.18 = 12.1 to 5.0 x 3.18 = 15.9 min.",
     "234.0 / 1.216 = 192.4 s = **3.21 min per recorded hour. This is the planning figure for the chosen part** (`design/firmware.md` line 718). A 10-hour day: 32.1 min. A full 4 GB card (16.9 hours, `design/firmware.md` line 718): 54.2 min. The ring's cell limits recording to 4.3 to 7.8 hours by ring size (`requirements.md` row P2): 4.3 x 3.21 = 13.8 to 7.8 x 3.21 = 25.0 min."),
    ("232.2 / 2.0 = 116.1 s = 1.94 min per recorded hour. The gain is 1.24 min per recorded hour.", "234.0 / 2.0 = 117.0 s = 1.95 min per recorded hour. The gain is 1.26 min per recorded hour."),
    ("the case copies 18.9 recorded hours (60 / 3.18), more than the ring can hold; the 3.8 to 5.0 recorded hours of one battery are copied in 12.1 to 15.9 min.",
     "the case copies 18.7 recorded hours (60 / 3.21), more than the ring can hold; the 4.3 to 7.8 recorded hours of one battery are copied in 13.8 to 25.0 min."),
]
for a, b in R:
    assert s.count(a) == 1, a[:60]
    ln = s[:s.index(a)].count("\n") + 1
    s = s.replace(a, b)
    print("case-architecture.md:%d\n  - %s\n  + %s" % (ln, a, b))
open(P, "w", encoding="utf-8").write(s)
