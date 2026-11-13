"""Attack firmware-check.py with faulty copies of firmware.md (copies live in review/fakes/; the real file is only read).
Expected result of every fake is written below BEFORE the run: each one is a faulty behaviour file, so the check must exit 1.
The honest control (an unchanged copy) must exit 0."""
import os, subprocess, sys
D = (__import__("pathlib").Path(__file__).resolve().parents[2].as_posix() + "/design")
OUT = D + "/review/fakes"
os.makedirs(OUT, exist_ok=True)
src = open(D + "/firmware.md", encoding="utf-8").read()

def rep(text, old, new, count=1):
    assert old in text, old
    return text.replace(old, new, count)

fakes = {}
fakes["control_unchanged"] = (src, 0)
# 1. a joystick centre press starts a recording (breaks the owner rule); count line kept consistent
t = rep(src, "| `STANDBY` | double press of the record button | `STANDBY` | nothing |",
        "| `STANDBY` | double press of the record button | `STANDBY` | nothing |\n| `STANDBY` | joystick centre press | `RECORDING` | open; M1 |")
t = rep(t, "The table has 60 transitions.", "The table has 61 transitions.")
fakes["joystick_starts_recording"] = (t, 1)
# 2. microphones powered in STANDBY (constant listening) in the state table
t = rep(src, "| `STANDBY` | idle, ready; nothing is captured | off |", "| `STANDBY` | idle, ready; nothing is captured | on |")
fakes["mic_on_in_standby_1_1"] = (t, 1)
# 3. microphones powered in STANDBY in the power table 8.2
t = rep(src, "| `STANDBY` | on | on | off | off |", "| `STANDBY` | on | on | on | off |")
fakes["mic_on_in_standby_8_2"] = (t, 1)
# 4. a short press stops a recording
t = rep(src, "| `RECORDING` | short press (a bump) | `RECORDING` | highlight marker; MH; screen 3 s with highlight count |",
        "| `RECORDING` | short press (a bump) | `STANDBY` | close; M2 |")
fakes["short_press_stops"] = (t, 1)
# 5. Bluetooth starts a recording (new row, count kept consistent)
t = rep(src, "| `RECORDING` | BLE control \"highlight\" from a bonded phone | `RECORDING` | highlight marker; MH |",
        "| `RECORDING` | BLE control \"highlight\" from a bonded phone | `RECORDING` | highlight marker; MH |\n| `STANDBY` | BLE control \"start\" from a bonded phone | `RECORDING` | open; M1 |")
t = rep(t, "The table has 60 transitions.", "The table has 61 transitions.")
fakes["ble_starts_recording"] = (t, 1)
# 6. the recording continues in the background after the stop press: RECORDING long press goes to RECORDING
t = rep(src, "| `RECORDING` | long press of the record button | `STANDBY` | close; M2 |",
        "| `RECORDING` | long press of the record button | `RECORDING` | screen off; keep recording |")
fakes["long_press_does_not_stop"] = (t, 1)
# 7. a timer starts a recording (new row, count consistent)
t = rep(src, "| `STANDBY` | battery reaches B15 | `STANDBY` | M3 once per discharge; status screen 5 s |",
        "| `STANDBY` | battery reaches B15 | `STANDBY` | M3 once per discharge; status screen 5 s |\n| `STANDBY` | GRTC timer every 60 min | `RECORDING` | open |")
t = rep(t, "The table has 60 transitions.", "The table has 61 transitions.")
fakes["timer_starts_recording"] = (t, 1)
# 8. the firmware gets a light pin and can switch the light off while recording
t = rep(src, "- No chip pin touches the light", "- The light is on P1.30 (LIGHT_EN) and the user may switch it off in settings. No chip pin touches the light")
fakes["light_pin_can_disable"] = (t, 1)

print("case | expected exit | got exit | last line")
mismatch = []
for name, (text, exp) in fakes.items():
    p = os.path.join(OUT, name + ".md")
    open(p, "w", encoding="utf-8").write(text)
    r = subprocess.run([D + "/.venv/bin/python", "-I", D + "/firmware-check.py", p], capture_output=True, text=True)
    open(os.path.join(OUT, name + ".log"), "w").write(r.stdout + r.stderr)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    print(f"{name} | {exp} | {r.returncode} | {last}")
    if r.returncode != exp:
        mismatch.append(name)
print("MISMATCH:", mismatch if mismatch else "none")
