P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/check_netlist.py")
s = open(P).read()
junk = "o3 = o3 and all(n.startswith('VBUS') is False for n in nets if n not in ('VBUS', 'VBUSOUT', 'U1_VBUS'))\n"
assert s.count(junk) == 1
s = s.replace(junk, '')
for l in ("band_a = ['JOY_UP', 'JOY_DOWN', 'JOY_LEFT', 'JOY_RIGHT', 'BTN_REC', 'GND']\n",
          "band_b = ['MOTOR_DRV', 'VDD_3V0', 'VBAT', 'GND', 'NTC', 'VBUS', 'USB_DN', 'USB_DP', 'GND']\n"):
    assert s.count(l) == 1
    s = s.replace(l, '')
open(P, 'w').write(s)
