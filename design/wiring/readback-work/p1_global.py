"""P1 frozen rule M4: a netlist reference absent from the fab data of every board of its netlist counts missing."""
import sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rb_lib as R
E = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad")
def refs_of(gdir, prefix):
    s = set()
    for n, p in R.find_board_files(gdir, prefix):
        L = R.parse_gerber(p)
        s |= set(f[3] for f in L.flashes if f[3]) | set(r[1] for r in L.regions if r[1])
    return s
ring = refs_of(E + '/ring/pcb/fab/gerber', 'ring')
band = set()
for d in sorted(glob.glob(E + '/band/fab/flex*-us*')):
    n = os.path.basename(d); band |= refs_of(d, n)
band.add('PRT1')
CS = os.path.dirname(os.path.abspath(__file__)) + '/src_b9ec3cfa/design/ecad/case'
cm = refs_of(CS + '/pcb/fab/case_main/gerber', 'case_main'); cp = refs_of(CS + '/pcb/fab/case_pins/gerber', 'case_pins')
for name, nl, present in (('ring netlist (ring + flex1 + flex2 boards)', E + '/ring/netlist.csv', ring | band), ('case netlist (case_main + case_pins)', CS + '/netlist.csv', cm | cp)):
    rows = R.read_netlist(nl); cnt = collections.Counter(r for _, r, _ in rows)
    ab = sorted(r for r in cnt if r not in present)
    print('GLOBAL %s: refs in netlist %d, absent from every board: %s (pad rows %d)' % (name, len(cnt), ab, sum(cnt[r] for r in ab)))
print('GLOBAL case_pins refs:', sorted(cp)); print('GLOBAL case_main has W1..:', sorted(r for r in cm if r.startswith('W')))
