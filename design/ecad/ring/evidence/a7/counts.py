"""Counts of the A7 tables against the saved A6 copies (evidence/a7/before/). Read with the csv module."""
import csv, os, collections
H = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring")
B = os.path.join(H, 'evidence', 'a7', 'before')
for tag, d in (('before', B), ('after', H)):
    n = list(csv.DictReader(open(os.path.join(d, 'netlist.csv'))))
    p = list(csv.DictReader(open(os.path.join(d, 'parts.csv'))))
    s = list(csv.DictReader(open(os.path.join(d, 'symbols.csv'))))
    a = list(csv.DictReader(open(os.path.join(d, 'additions.csv'))))
    o = list(csv.DictReader(open(os.path.join(d, 'open-pins.csv'))))
    k = collections.Counter(x['kind'] for x in a)
    ok = collections.Counter(x['reference'] for x in o)
    print(tag, 'netlist rows', len(n), 'nets', len({x['net'] for x in n if x['net']}),
          'no-connect pins', sum(1 for x in n if x['pin_type'] == 'no_connect'), 'parts', len(p),
          'symbols', len({x['symbol'] for x in s}), 'additions', dict(k), 'open-pins rows', len(o),
          'open-pins pin rows', sum(1 for x in o if x['pin_number']), 'open-pins U2 rows', ok.get('U2', 0))
    print(tag, 'open-pins rows by reference', dict(ok))
