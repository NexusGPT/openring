"""run_p1.py <board> [fabroot]: P1 read-back of one board (Route B Gerber/drill, Route A IPC-D-356 for the ring).
Prints one line per figure; writes results/p1_<board>.json. Never edits design files."""
import sys, os, glob, json, re, time, csv, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rb_lib as R
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad")
LINES = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring")  # ring-apply-a2 copy: the ring's own netlist; fab from env RBFAB
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
# the version under test is commit b9ec3cfa; the case folder of the working tree was being edited by another agent during the run, so the case
# files are read from a git archive of that commit extracted into the work folder (src_b9ec3cfa)
CASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src_b9ec3cfa/design/ecad/case')

PRT1 = [('VBAT', 'PRT1', '1'), ('GND', 'PRT1', '2'), ('NTC', 'PRT1', '3')]   # band-interface.md lines 111-113, build_band.py line 345


def spec(board, fab=None):
    if board == 'ring':
        F = fab or os.environ['RBFAB']
        return dict(gerber=F + '/gerber', prefix='ring', drills=sorted(glob.glob(F + '/drill/*.drl')), nl=LINES + '/netlist.csv', scope=None, extra=[], res=0.005)
    if board in ('case_main', 'case_pins'):
        F = fab or CASE + '/pcb/fab/' + board
        # D1 (pilot finding, see board-readback.md): the pin board's wire pads are named WP1..WP7; the netlist names the wire W1..W7.
        # Pairing: build_boards.py line 61 WIRE_ENDS = {"WP1": "W1", "WP2": "W2", "WP3": "W3", "WP4": "W4", "WP7": "W7"}
        extra = []
        if board == 'case_pins':
            nlr = R.read_netlist(CASE + '/netlist.csv')
            for wp, w in (('WP1', 'W1'), ('WP2', 'W2'), ('WP3', 'W3'), ('WP4', 'W4'), ('WP7', 'W7')):
                extra += [(n, wp, '1') for n, r_, p_ in nlr if r_ == w and p_ == '1']
        return dict(gerber=F + '/gerber', prefix=board, drills=sorted(glob.glob(F + '/gerber/*.drl')), nl=CASE + '/netlist.csv', scope=None, extra=extra, res=0.010)
    m = re.match(r'(flex[12])-us(\d+)$', board)
    if m:
        F = fab or ROOT + '/band/fab/' + board
        scope = {'flex1': {'J_BAND_A', 'M1', 'SW1', 'SW2', 'SW3', 'SW4', 'SW5'}, 'flex2': {'J_BAND_B', 'CP1', 'CP2', 'CP3', 'CP4'}}[m.group(1)]
        return dict(gerber=F, prefix=board, drills=sorted(glob.glob(F + '/*.drl')), nl=ROOT + '/ring/netlist.csv',
                    scope=scope | ({'PRT1'} if m.group(1) == 'flex2' else set()), extra=PRT1 if m.group(1) == 'flex2' else [], res=0.005)
    raise SystemExit('unknown board ' + board)


def parse_ipc(path):
    pads, vias = [], []
    for ln in open(path):
        code = ln[:3]
        if code not in ('317', '327', '307'):
            continue
        net = ln[3:17].strip()
        m = re.search(r'A(\d\d)X([+-]\d+)Y([+-]\d+)', ln)
        x, y = int(m.group(2)) * 0.00254, int(m.group(3)) * 0.00254
        if ln[20:23] == 'VIA':
            vias.append((net, x, y)); continue
        ref = ln[20:26].strip(); pin = ln[27:31].strip()   # fixed columns of IPC-D-356A (reference 6 characters)
        pads.append((net, ref, pin, x, y))
    return pads, vias


def run(board, fab=None, tag=None, log=print):
    sp = spec(board, fab)
    t0 = time.time()
    lp = R.find_board_files(sp['gerber'], sp['prefix'])
    b = R.Board(board, lp, sp['drills'], res=sp['res'])
    rows = R.read_netlist(sp['nl']) + sp['extra']
    st = b.connectivity(barrel=True)
    c = R.compare(b, rows, sp['scope'])
    res = dict(board=board, tag=tag, layers=[n for n, _ in lp], raster_um=sp['res'] * 1000, size=[b.W, b.H], stats=st)
    res.update({k: v for k, v in c.items() if k not in ('net_groups', 'grp_nets', 'short_groups', 'open_nets', 'nc_touch', 'missing_pads', 'unlisted_pads')})
    res['open_nets'] = c['open_nets']; res['short_groups'] = c['short_groups']; res['nc_touch'] = c['nc_touch']
    res['missing_pads'] = ['%s-%s' % k for k in c['missing_pads']]; res['unlisted_pads'] = ['%s-%s' % k for k in c['unlisted_pads']]
    # alternative (stack of microvias) model
    b2 = R.Board(board, lp, sp['drills'], res=sp['res'])
    st2 = b2.connectivity(barrel=False)
    c2 = R.compare(b2, rows, sp['scope'])
    res['stack_model'] = dict(stats=st2, shorts=c2['shorts'], opens=c2['opens'], open_nets=c2['open_nets'])
    # label (TO.N) versus geometry
    pads = b.pads()
    exp = {(r, p): n for n, r, p in rows}
    lab_mis = []
    for p in pads:
        e = exp.get((p['ref'], p['pin']))
        if e is None:
            continue
        a = p['netattr']
        if (a or '') != (e or '') and not (e == '' and a in ('N/C', None, '')):
            lab_mis.append((p['ref'], p['pin'], a, e))
    res['label_vs_netlist_mismatch'] = lab_mis
    # draws: attribute net vs the nets of the group the draw sits in
    gm = [b.group_map(k) for k in range(len(b.layers))]
    grp_nets = c['grp_nets']
    d_mis, d_tot = 0, 0
    for k, L in enumerate(b.layers):
        for (x1, y1, x2, y2, w, na) in L.draws:
            i, j = b.ij((x1 + x2) / 2, (y1 + y2) / 2)
            g = int(gm[k][b.labs[k][i, j]]) if b.labs[k][i, j] else None
            d_tot += 1
            ns = grp_nets.get(g, set())
            if ns and (na not in ns):
                d_mis += 1
    res['draws_checked'] = d_tot; res['draw_label_mismatch'] = d_mis
    # Route A (ring only)
    if board == 'ring' and (fab or True):
        ipc = (fab or ROOT + '/ring/pcb/fab') + '/ring.ipc356'
        if os.path.exists(ipc):
            ip, iv = parse_ipc(ipc)
            # the IPC-D-356 reference field is 6 characters: J_BAND_A / J_BAND_B both read 'J_BAND'. Resolve each truncated
            # reference from the Gerber flash at the same place (finding F-IPC-REF, reported)
            allp = {}
            for q in pads:
                allp.setdefault((q['ref'][:6], q['pin']), []).append(q)
            ip2, trunc = [], 0
            for net, r, p_, x, y in ip:
                cands = [q for q in allp.get((r[:6], p_), [])]
                if cands:
                    q = min(cands, key=lambda q: (q['x'] - x) ** 2 + (q['y'] - y) ** 2)
                    if ((q['x'] - x) ** 2 + (q['y'] - y) ** 2) ** 0.5 <= 0.05 and q['ref'] != r:
                        r = q['ref']; trunc += 1
                ip2.append((net, r, p_, x, y))
            ip = ip2
            res['ipc_truncated_refs_resolved'] = trunc
            iexp = {(r, p): n for n, r, p in rows}
            refs_here = set(r for _, r, _, _, _ in ip)
            ipn = {}
            for net, r, p, x, y in ip:
                ipn[(r, p)] = net
            exp_here = {k: v for k, v in iexp.items() if k[0] in refs_here}
            only_ipc = sorted(set(ipn) - set(exp_here)); only_nl = sorted(set(exp_here) - set(ipn))
            # partition compare over common pads
            common = sorted(set(ipn) & set(exp_here))
            def part(m):
                g = {}
                for k in common:
                    n = m[k]
                    if n in ('', 'N/C'):
                        g[('single', k)] = {k}
                    else:
                        g.setdefault(n, set()).add(k)
                return sorted(sorted(v) for v in g.values())
            pa, pb = part(ipn), part(exp_here)
            sa = set(map(tuple, pa)); sb = set(map(tuple, pb))
            joined = [g for g in sa - sb]; split = [g for g in sb - sa]
            # coordinates: every IPC pad against a Gerber flash of the same ref/pin
            byrp = {}
            for p in pads:
                byrp.setdefault((p['ref'], p['pin']), []).append(p)
            coord_bad, coord_ok = [], 0
            for net, r, p, x, y in ip:
                cands = byrp.get((r, p), [])
                best = min([((q['x'] - x) ** 2 + (q['y'] - y) ** 2) ** 0.5 for q in cands], default=None)
                if best is not None and best <= 0.05:
                    coord_ok += 1
                else:
                    coord_bad.append((r, p, best))
            res['routeA'] = dict(ipc_pad_records=len(ip), ipc_via_records=len(iv), nets=len(set(n for n in ipn.values() if n not in ('N/C', ''))),
                                 pads_compared=len(common), pads_only_in_ipc=['%s-%s' % k for k in only_ipc], pads_only_in_netlist=['%s-%s' % k for k in only_nl],
                                 groups_joined_or_differing=len(joined), groups_split_or_differing=len(split),
                                 joined_examples=[g[:3] for g in joined[:5]], split_examples=[g[:3] for g in split[:5]],
                                 coord_match=coord_ok, coord_bad=coord_bad[:10], coord_bad_n=len(coord_bad))
    res['seconds'] = round(time.time() - t0, 1)
    res['when'] = datetime.datetime.now().isoformat(timespec='seconds')
    name = 'p1_%s%s.json' % (board, ('_' + tag) if tag else '')
    json.dump(res, open(os.path.join(OUT, name), 'w'), indent=1, default=str)
    log('P1 board=%s tag=%s routeB nets=%d pads=%d shorts=%d opens=%d missing=%d absent_refs=%s' % (board, tag, res['nets'], res['pads'], res['shorts'], res['opens'], res['missing'], res['absent_refs']))
    log('   stack_model shorts=%d opens=%d; hole stats %s; label_vs_netlist_mismatch=%d; draws checked=%d label mismatch=%d' % (res['stack_model']['shorts'], res['stack_model']['opens'], st, len(lab_mis), d_tot, d_mis))
    if 'routeA' in res:
        a = res['routeA']
        log('   routeA ipc pads=%d vias=%d nets=%d compared=%d only_ipc=%s only_netlist=%s joined=%d split=%d coord_match=%d coord_bad=%d' % (a['ipc_pad_records'], a['ipc_via_records'], a['nets'], a['pads_compared'], a['pads_only_in_ipc'], a['pads_only_in_netlist'], a['groups_joined_or_differing'], a['groups_split_or_differing'], a['coord_match'], a['coord_bad_n']))
    return res


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None, sys.argv[3] if len(sys.argv) > 3 else None)
    print('P1_DONE', sys.argv[1])
