# B3: each board's pads carry the nets of its netlist (own script; pads from dump_pads.py).
# For every netlist row whose part sits on the board: the pad exists and has the netlist's net.
# For every pad with a net on the board: a netlist row of that part and pin says the same net.
# Parts that the design solders only on some terminals (SW1, SW3, SW4, SW5 terminals 1 and 2,
# band-interface.md line 103) are listed as such, not hidden.
import csv, collections
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
import os
W = os.environ.get('WDIR', R + '/design/wiring/review-work')
def netl(nl):
    d = {}
    for r in csv.DictReader(open(f'{R}/design/ecad/{nl}/netlist.csv')):
        d[(r['reference'], r['pin_number'])] = r['net']
    return d
NL = {'ring': netl('ring'), 'case': netl('case')}
boards = [('ring', 'ring')] + [(f'flex{f}-us{s}', 'ring') for f in (1, 2) for s in range(7, 14)] + [('case_main', 'case'), ('case_pins', 'case')]
# PRT1 on FLEX2 stands for the pack's outputs (band-interface.md lines 111 to 113)
ALIAS = {('PRT1', '1'): ('BT1', '1'), ('PRT1', '2'): ('BT1', '2'), ('PRT1', '3'): ('RT1', '1')}
total = collections.Counter()
for b, nl in boards:
    pads = {}
    for r in csv.DictReader(open(f'{W}/pads/{b}.csv')):
        pads.setdefault((r['ref'], r['pad']), set()).add(r['net'])
    refs = {k[0] for k in pads}
    bad = []; missing = []; extra = []; ok = 0
    for (ref, pin), net in NL[nl].items():
        if ref not in refs:
            continue
        if (ref, pin) not in pads:
            missing.append(f'{ref}:{pin}({net})'); continue
        if pads[(ref, pin)] != {net}:
            bad.append(f'{ref}:{pin} board {sorted(pads[(ref, pin)])} netlist {net!r}')
        else:
            ok += 1
    for (ref, pin), nets in pads.items():
        key = ALIAS.get((ref, pin), (ref, pin))
        if key not in NL[nl]:
            if nets != {''}:
                extra.append(f'{ref}:{pin}({",".join(sorted(nets))})')
        elif ALIAS.get((ref, pin)) and nets != {NL[nl][key]}:
            bad.append(f'{ref}:{pin} board {sorted(nets)} netlist via {key} {NL[nl][key]!r}')
        elif ALIAS.get((ref, pin)):
            ok += 1
    total['ok'] += ok; total['bad'] += len(bad); total['extra'] += len(extra)
    print(f'{b}: netlist pins matched {ok}; wrong net {len(bad)} {bad}; netlist pins with no pad {len(missing)} {missing}; pads with a net but no netlist row {len(extra)} {extra}')
print('TOTAL', dict(total))
