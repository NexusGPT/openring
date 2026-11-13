#!/usr/bin/env python3
"""Final audit: pulls every quoted phrase, every number with a decimal point or unit, and every path named W/... or
logs/... or stepped/... from the given claim files, and searches the evidence tree (W without the claim files) for each.
Prints each claim with the first evidence file and line that holds it, every claim with no match, and the em dash count."""
import os, re, sys
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring-circuit-work")
claims_files = sys.argv[1:]
skip = set(os.path.abspath(p) for p in claims_files) | {os.path.join(W, 'CHECKLIST.md'), os.path.join(W, 'logs', 'audit_phase1.txt')}
ev = []
for root, dirs, files in os.walk(W):
    dirs[:] = [d for d in dirs if d not in ('run', 'diag_run')]
    for f in files:
        p = os.path.join(root, f)
        if p in skip or os.path.islink(p) or os.path.getsize(p) > 3_000_000:
            continue
        try:
            ev.append((p, open(p, errors='replace').read().split('\n')))
        except Exception:
            pass
# real files cited by repo path also count as evidence
for rp in ('design/ecad/ring/check_netlist.py', 'design/ecad/ring/pcb/u4-capacitors.md', 'design/wiring/lead-decisions.md',
           'design/sim/circuit/results/summary.txt', 'design/sim/circuit/results/stepped/stepped_compare.csv',
           'design/sim/circuit/results/info.txt', 'design/sim/circuit/results/rows.csv', 'design/sim/circuit/logs/stepped_enable_c2.log',
           'design/ecad/ring/evidence/check_c2.log', 'design/ecad/ring/erc-report.txt', 'design/sim/circuit/models/npm1304.lib',
           'design/sim/circuit/decks/stepped/pass-line.md', 'design/ecad/ring/make_netlist.py', 'design/bom.csv'):
    p = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/") + rp
    ev.append((p, open(p, errors='replace').read().split('\n')))
def find(s):
    for p, lines in ev:
        for i, l in enumerate(lines, 1):
            if s in l:
                return '%s:%d' % (p.replace(W + '/', 'W/'), i)
    return None
n = miss = 0
for cf in claims_files:
    t = open(cf).read()
    print('== claims of', cf, '; em dashes:', t.count('—'))
    items = re.findall(r'"([^"\n]{3,120})"', t)
    items += re.findall(r'(?<![\w.])(\d+\.\d+)(?![\w])', t)
    items += [m for m in re.findall(r'\b((?:logs|stepped|bench_base|bench_patched|patched2?|base)/[\w./-]+[\w])', t)]
    for it in dict.fromkeys(items):
        n += 1
        if '/' in it and not it.startswith('"') and os.path.exists(os.path.join(W, it)):
            print('ok   path exists: %s' % it); continue
        hit = find(it)
        if hit:
            print('ok   %-60s %s' % (it[:60], hit))
        else:
            miss += 1
            print('MISS %s' % it)
print('claims checked %d, with no match %d' % (n, miss))
