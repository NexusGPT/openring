"""compare_expected.py <check log>: compares a run of check_light_path.py with logs/expected_run1.txt; prints each case that differs."""
import re
import sys

t = open(sys.argv[1]).read()
exp = [
    ("RESULT PASS", r"^RESULT PASS$"),
    ("LED1 body gap 0.350", r"LED1 body clear .*? at 0\.350 mm"),
    ("LED1 pads gap 0.350", r"LED1 pad 1 clear .*? at 0\.350 mm"),
    ("guide bar gap 0.300", r"guide LG1 bar clear .*? at 0\.300 mm"),
    ("riser gap 0.350", r"guide LG1 riser clear .*? at 0\.350 mm"),
    ("hole gap 0.250", r"board hole clear .*? at 0\.250 mm"),
    ("hole to pads 0.225", r"board hole to LED1 pads .*?: 0\.225 mm"),
    ("riser top 0.100", r"riser top below .*?: 0\.100 mm"),
    ("LP1 to bond 0.100", r"LP1 clear of the FPC bond .*?gap 0\.100"),
    ("LP1 to IC 0.100", r"LP1 clear of the driver IC .*?gap 0\.100"),
    ("fingers 0.100", r"bond fingers .*?gap 0\.100"),
    ("R41 820 ohm about 1.50 mA", r"E24 820 ohm gives 1\.50\d mA"),
    ("680 ohm about 1.81 mA", r"680 ohm gives 1\.81\d mA"),
    ("v4 window over the bond: yes", r"over the FPC bond of the maker drawing: yes"),
]
n_diff = 0
for name, pat in exp:
    if not re.search(pat, t, re.M):
        n_diff += 1
        print(f"DIFFERS: {name}")
named = re.findall(r"nearest (\w+) at", t)
print(f"nearest-part names reported: {sorted(set(named))} (expected J1 = screen_connector for LED, pads, riser; J1 or mic_1 for bar and hole)")
print(f"cases compared: {len(exp)}, differing: {n_diff}")
