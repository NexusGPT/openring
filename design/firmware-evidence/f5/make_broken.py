"""Make broken copies of the delivered firmware.md, each with exactly one F5 fact reverted.
Writes broken/<name>.md and prints what changed. Expected FAIL texts are in expected_broken.txt
(written before the run)."""
import os
import sys

src, outdir = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
os.makedirs(outdir, exist_ok=True)
cases = {
    "b1_charge_current": ("`CHARGE_CURRENT` = 15,000 (15 mA", "`CHARGE_CURRENT` = 20,000 (15 mA"),
    "b2_motor_q1": ("- **Drive** (architecture 17.22;", "- **Drive** through Q1 (architecture 17.22;"),
    "b3_ship_hibernate": ("4. Write TASKENTERSHIPMODE = 1 [NPM p118].", "4. Call `mfd_npm13xx_hibernate()` with the longest timer the driver accepts, 74.6 hours."),
    "b4_battery_range": ("Hours on the smallest cell, 18.2 mAh at US 7", "Hours on 15 to 20 mAh at US 7"),
    "b5_pin": ("| Microphones 1 and 2 (one stereo input) | `pdm20` | MIC_A_CLK P1.13,", "| Microphones 1 and 2 (one stereo input) | `pdm20` | MIC_A_CLK P1.11,"),
    "b6_mic_part": ("receives U5 (SELECT on GND)", "receives U5 (SELECT on GND) of the IM68D128B"),
    "b7_power_chip_name": ("### 8.1 nPM1304 settings", "### 8.1 nPM1300 settings"),
    "b8_protocol_sentence": ("The link protocol is being specified separately (design/protocol/) and is not accepted yet; nothing of it is in F5.\n\n", ""),
    "b9_ship_vbus": ("3. If VBUS is present, wait for the event EVENTVBUSREMOVED", "3. If VBUS is present, go on at once"),
}
for name, (a, b) in cases.items():
    n = s.count(a)
    t = s.replace(a, b, 1)
    open(os.path.join(outdir, name + ".md"), "w", encoding="utf-8").write(t)
    print(f"{name}: occurrences of the original text {n}; copy differs from the original: {t != s}")
