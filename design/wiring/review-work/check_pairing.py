# B2 pairing across the spring pins, own computation at every size.
# Ring side: the inside model's rule (thin.py lines 66, 733-734, 740, 872: pads VBUS, D-, D+, GND at arc
# offsets (-1.5+k)*2.4 mm round the bore's bottom, VBUS first = lowest angle = +Y side), bore per size
# from thin.py SIZE_TABLE; cross-checked with each flex2 board's CP order along the tail.
# Case side: the pin board file (pads/case_pins.csv): pin y in the case frame = 100 - KiCad x
# (P1 at x 96.479 <-> case y +3.521, case-architecture.md line 205), nets from the board.
import csv, math
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/review-work")
BORE = {7: 17.3196, 8: 18.1324, 9: 18.9452, 10: 19.7580, 11: 20.5708, 12: 21.3836, 13: 22.1964}
ring_net = {'VBUS': 'VBUS', 'D-': 'USB_DN', 'D+': 'USB_DP', 'GND': 'GND'}
want = {'VBUS': 'VRING', 'USB_DN': 'USB_D-', 'USB_DP': 'USB_D+', 'GND': 'GND'}
pins = [r for r in csv.DictReader(open(f'{W}/pads/case_pins.csv')) if r['ref'] in ('P1', 'P2', 'P3', 'P4')]
pin_y = {r['ref']: (100.0 - float(r['x_mm']), r['net']) for r in pins}
fails = 0
for s, bore in BORE.items():
    r_in = bore / 2
    # flex2 board order of the pads along the tail (CP1 first = nearest the slot = +Y)
    cps = sorted([r for r in csv.DictReader(open(f'{W}/pads/flex2-us{s}.csv')) if r['ref'].startswith('CP')], key=lambda r: float(r['x_mm']))
    order = [r['net'] for r in cps]
    for k, nm in enumerate(('VBUS', 'D-', 'D+', 'GND')):
        o = (-1.5 + k) * 2.4
        y = r_in * math.sin(-o / r_in)   # angle 180 + o/R from the top; at the bottom +Y for negative offset
        near = min(pin_y, key=lambda p: abs(pin_y[p][0] - y))
        py, pnet = pin_y[near]
        ok = pnet == want[ring_net[nm]] and abs(py - y) < 0.2 and order[k] == ring_net[nm]
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} US{s} pad {nm} ({ring_net[nm]}, flex2 order {k+1}: {order[k]}) at case y {y:+.3f} -> nearest pin {near} y {py:+.3f} net {pnet} offset {abs(py-y):.3f}")
print(f'RESULT pairing fails={fails} of 28')
