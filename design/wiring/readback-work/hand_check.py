"""compares the hand labels with the scorer's net for the same pad (net of the pads in the Gerber-derived component)"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_p1 as P, rb_lib as R
rows = list(csv.DictReader(open(os.path.dirname(os.path.abspath(__file__)) + '/hand_labels.csv')))
cache = {}
agree = 0
for r in rows:
    bd = r['board']
    if bd not in cache:
        sp = P.spec(bd); lp = R.find_board_files(sp['gerber'], sp['prefix'])
        b = R.Board(bd, lp, sp['drills'], res=sp['res']); b.connectivity()
        nl = R.read_netlist(sp['nl']) + sp['extra']
        c = R.compare(b, nl, sp['scope'])
        cache[bd] = (b, c)
    b, c = cache[bd]
    ps = [p for p in b.pads() if p['ref'] == r['ref'] and p['pin'] == r['pin']]
    nets = set()
    for p in ps:
        nets |= c['grp_nets'].get(p['group'], set())
    ok = (nets == {r['label_net_read_by_hand']})
    agree += ok
    print('HAND %-11s %-9s %-4s label=%-9s scorer_nets=%s %s' % (bd, r['ref'], r['pin'], r['label_net_read_by_hand'], sorted(nets), 'AGREE' if ok else 'DISAGREE'))
print('HAND agreement %d of %d' % (agree, len(rows)))
