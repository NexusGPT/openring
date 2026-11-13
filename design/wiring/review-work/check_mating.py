# B5: each band circuit's tail lands against the main board's J_BAND lands, land by land.
# Fits the best 2D rigid map (rotation + shift, with or without a mirror) from the tail land centres
# to the main board land centres of the SAME number, and prints both residuals.
# Physics: the main board file is drawn seen from its land face (F.Cu, looking up from the floor);
# the tail file is drawn seen from its land face (F.Cu). Laid face to face, the true map between the
# two drawings MUST be a mirror (determinant -1). A pattern that matches only without a mirror is wrong.
# Also prints where the rest of the tail (its other parts) falls under the mirror fit: it must lie
# outward of the lands (|Y| larger, toward the slot), not across the board.
import csv, math, sys
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = R + '/design/wiring/review-work'
def pads(name):
    return list(csv.DictReader(open(f'{W}/pads/{name}.csv')))
ring = pads('ring')
def fit(P, Q, mirror):
    # P, Q lists of (x, y); find R (rotation, optional mirror) and t minimising |R p + t - q|
    if mirror:
        P = [(x, -y) for x, y in P]
    n = len(P)
    pcx = sum(p[0] for p in P) / n; pcy = sum(p[1] for p in P) / n
    qcx = sum(q[0] for q in Q) / n; qcy = sum(q[1] for q in Q) / n
    s_cos = s_sin = 0.0
    for (px, py), (qx, qy) in zip(P, Q):
        ax, ay = px - pcx, py - pcy; bx, by = qx - qcx, qy - qcy
        s_cos += ax * bx + ay * by; s_sin += ax * by - ay * bx
    th = math.atan2(s_sin, s_cos)
    c, s = math.cos(th), math.sin(th)
    def m(p):
        x, y = (p[0], -p[1]) if mirror else p
        x -= pcx; y -= pcy
        return (c * x - s * y + qcx, s * x + c * y + qcy)
    worst = max(math.hypot(m(p0)[0] - q[0], m(p0)[1] - q[1]) for p0, q in zip(Porig, Q))
    return worst, m, math.degrees(th)
fails = 0
for tail, jref in (('flex1', 'J_BAND_A'), ('flex2', 'J_BAND_B')):
    rb = {r['pad']: r for r in ring if r['ref'] == jref}
    for s in (7, 8, 9, 10, 11, 12, 13):
        fb = pads(f'{tail}-us{s}')
        tb = {r['pad']: r for r in fb if r['ref'] == jref}
        nums = sorted(set(rb) | set(tb), key=lambda v: int(v))
        if set(rb) != set(tb):
            print(f'FAIL {tail}-us{s} land numbers differ: main {sorted(rb)} tail {sorted(tb)}'); fails += 1; continue
        Porig = [(float(tb[k]['x_mm']), float(tb[k]['y_mm'])) for k in nums]
        Q = [(float(rb[k]['x_mm']), float(rb[k]['y_mm'])) for k in nums]
        w_m, map_m, th_m = fit(Porig, Q, True)
        w_p, map_p, th_p = fit(Porig, Q, False)
        netok = all(tb[k]['net'] == rb[k]['net'] for k in nums)
        # where the other tail parts land under the mirror map (model Y = KiCad y - 100)
        others = [r for r in fb if r['ref'] != jref]
        ys = [map_m((float(r['x_mm']), float(r['y_mm'])))[1] - 100 for r in others]
        land_y = [q[1] - 100 for q in Q]
        outward = (min(abs(y) for y in ys) > max(abs(y) for y in land_y)) if ys else None
        sameside = all((y > 0) == (land_y[0] > 0) for y in ys)
        ok = w_m < 0.05 and netok and outward and sameside
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} {tail}-us{s} {jref}: lands {len(nums)}; mirror fit worst {w_m:.4f} mm (rot {th_m:.1f}); "
              f"no-mirror fit worst {w_p:.4f} mm; nets equal land by land {netok}; rest of tail |Y| from {min(abs(y) for y in ys):.2f} "
              f"(lands |Y| to {max(abs(y) for y in land_y):.3f}) outward {outward}, same side {sameside}")
print(f'RESULT mating fails={fails} of 14')
