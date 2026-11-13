"""Writes ONE broken copy of netlist.csv for the A7 failure proof (evidence/a7/broken/netlist_broken.csv).
Each break targets one A7 check; expected FAIL tags are written to broken/expected.txt before the run."""
import csv, os
HERE = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring")
OUT = os.path.join(HERE, 'evidence', 'a7', 'broken')
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(HERE, 'netlist.csv'))))
BREAK = {  # (ref, pin) -> new net, with the check it must trip
    ('U2', 'D1'): ('GND', 'A7-1'),      # a U2 VBAT ball moved to ground
    ('U11', '4'): ('VDD_3V0', 'A7-2'),  # motor regulator input on the 3.0 V rail, not the cell
    ('U5', '5'): ('VDD_MIC', 'A7-3'),   # a microphone GROUND pin on the supply
    ('C71', '1'): ('VSYS', 'A7-4'),     # the 25 V VBUS capacitor moved off VBUS
    ('LED1', '1'): ('LED_A', 'A7-5'),   # LED polarity reversed
    ('LED1', '2'): ('LED_K', 'A7-5'),
}
hit = set()
for r in rows:
    k = (r['reference'], r['pin_number'])
    if k in BREAK:
        print('break %s.%s %s -> %s' % (k[0], k[1], r['net'], BREAK[k][0]))
        r['net'] = BREAK[k][0]; hit.add(k)
assert hit == set(BREAK), hit
with open(os.path.join(OUT, 'netlist_broken.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT, 'expected.txt'), 'w') as f:
    f.write('expected: exit 1; FAIL lines tagged %s; also the KiCad compare fails (the sheets are the good ones)\n'
            % ', '.join(sorted(set(t for _, t in BREAK.values()))))
print(open(os.path.join(OUT, 'expected.txt')).read())
