"""pads with a net on each case board vs the rows of netlist.csv (same question as the review's check_parity.py: 'pads with a net but no netlist row').
usage: parity.py netlist.csv dump.log   (dump.log from dump_pins.py: lines 'PAD ref number net layers ...')"""
import csv, re, sys
nl = {(r['reference'], r['pin_number']): r['net'] for r in csv.DictReader(open(sys.argv[1]))}
extra, wrong, n = [], [], 0
for l in open(sys.argv[2]):
    m = re.match(r'PAD (\S+) (\S*) (\S*) layers', l)
    if not m:
        m2 = re.match(r'PAD (\S+) (\S+)\s+layers', l)   # pad without number or net
        continue
    ref, num, net = m.groups()
    if not net or not num:
        continue
    n += 1
    if (ref, num) not in nl:
        extra.append('%s:%s(%s)' % (ref, num, net))
    elif nl[(ref, num)] != net:
        wrong.append('%s:%s board %s netlist %s' % (ref, num, net, nl[(ref, num)]))
print('%s: pads with a net %d; pads with a net but no netlist row %d %s; wrong net %d %s' % (sys.argv[2].split('/')[-1], n, len(extra), extra, len(wrong), wrong))
