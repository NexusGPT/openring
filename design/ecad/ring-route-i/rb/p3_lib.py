import sys, os, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rb_lib as R, rb_res as S, run_p1 as P


def load(board, copper_um=None):
    sp = P.spec(board)
    lp = R.find_board_files(sp['gerber'], sp['prefix'])
    b = R.Board(board, lp, sp['drills'], res=sp['res'])
    b.connectivity()
    rows = R.read_netlist(sp['nl']) + sp['extra']
    c = R.compare(b, rows, sp['scope'])
    return b, c, rows


def net_group(c, net):
    g = c['net_groups'][net]
    assert len(g) == 1, (net, len(g))
    return next(iter(g))


def path_R(b, c, net, src, snks, rs, log, label, currents, mesh=None, graph=None):
    """src: [(ref,pin)], snks: [[(ref,pin),...]] one merged sink group per entry. returns list of dicts"""
    g = net_group(c, net)
    if mesh is None:
        mesh = S.build_mesh(b, g, rs)
    if graph is None:
        gmaps = [b.group_map(k) for k in range(len(b.layers))]
        def ok(k, x, y):
            i, j = b.ij(x, y)
            l = b.labs[k][i, j]
            return bool(l) and int(gmaps[k][l]) == g
        graph = S.DGraph(b, ok, rs)
    out = []
    sn = S.pad_nodes(b, mesh, src)
    for sk in snks:
        kn = S.pad_nodes(b, mesh, sk)
        if not sn or not kn:
            out.append(dict(label=label, sink=sk, error='no pad nodes src=%d snk=%d' % (len(sn), len(kn))))
            log('P3 %s | %s -> %s | ERROR no pad nodes (src %d, snk %d)' % (label, src, sk, len(sn), len(kn)))
            continue
        R_, nfree = S.resistance(mesh, sn, kn)
        def gnodes(pads):
            ns = []
            for (ref, pin) in pads:
                for k, L in enumerate(b.layers):
                    for f in L.flashes:
                        if f[3] == ref and f[4] == pin:
                            kk = graph.key(k, f[0], f[1])
                            if kk in graph.adj:
                                ns.append(kk)
            return ns
        gs, gk = gnodes(src), gnodes(sk)
        sp_ = graph.shortest(gs, gk, by='res') if gs and gk else None
        rec = dict(zone_regions=zone_copper(b, g), label=label, net=net, src=['%s-%s' % p for p in src], sink=['%s-%s' % p for p in sk], R_mesh_mohm=R_ * 1e3, nodes=mesh['N'], vias=mesh['nvia'],
                   R_tracksum_mohm=(sp_[2] * 1e3 if sp_ else None), len_mm=(sp_[1] if sp_ else None))
        rec['drops_mV'] = {('%gmA' % (I * 1e3)): R_ * I * 1e3 for I in currents}
        out.append(rec)
        log('P3 %s | %s -> %s | R(mesh)=%.2f mohm | R(drawn tracks on min-R path)=%s mohm, path length %s mm | %s | mesh nodes %d, hole joins %d | zone regions in net %d' % (
            label, '+'.join(rec['src']), '+'.join(rec['sink']), rec['R_mesh_mohm'],
            ('%.2f' % rec['R_tracksum_mohm']) if rec['R_tracksum_mohm'] is not None else 'n/a', ('%.3f' % rec['len_mm']) if rec['len_mm'] is not None else 'n/a',
            ' ; '.join('drop at %s = %.2f mV' % (k, v) for k, v in rec['drops_mV'].items()), mesh['N'], mesh['nvia'], rec['zone_regions']))
    return out, mesh, graph


def zone_copper(b, g):
    """number of G36 regions (zone fills) whose vertex pixels lie in group g"""
    n = 0
    for k, L in enumerate(b.layers):
        gm = b.group_map(k)
        for (rg, ref, pin, na) in L.regions:
            hit = False
            for (x, y) in rg[:12]:
                i, j = b.ij(x, y)
                if 0 <= i < b.H and 0 <= j < b.W and b.labs[k][i, j] and int(gm[b.labs[k][i, j]]) == g:
                    hit = True; break
            n += hit
    return n


def net_pads(rows, net, scope_refs=None):
    return [(r, p) for n, r, p in rows if n == net and (scope_refs is None or r in scope_refs)]
