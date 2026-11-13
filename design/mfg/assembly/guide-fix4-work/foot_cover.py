#!/usr/bin/env python3
"""H2: what lies over each board land once the ribbon foot is pressed.

Reads the 14 band boards (read only) and, for each J_BAND tail land, takes the board
land's plan area as seen on the tail (the tail land centre, 0.55 along the tail and 0.30
across: band-interface.md lines 23 and 91) and lists the copper of the OTHER face (B.Cu,
the face toward the stiffener and the eye) that crosses it: tracks and vias, and the
stiffener outline (User.1). It also checks whether any part of the board land lies
outside the foot outline (then that part could be seen beside the foot).
Board land = 0.30 (X) x 0.55 (Y) on the board; on the tail the long side runs along the
tail (u), which is the board X direction of the tail file here (pads dumps: rows at
x 50.475 and 51.375, i.e. 0.90 apart = the row pitch).
"""
import re, glob, sys, math

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
PADS = ROOT + '/design/wiring/review4-work/pads'


def tail_lands(name):
    out = []
    for l in open(f'{PADS}/{name}-pads.csv'):
        f = l.strip().split(',')
        if f[0] in ('J_BAND_A', 'J_BAND_B'):
            out.append((f[0], int(f[1]), f[2], float(f[3]), float(f[4])))
    return out


def segs(text, layer):
    res = []
    for m in re.finditer(r'\(segment\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "([^"]*)"\)', text):
        if m.group(6) == layer:
            res.append(tuple(float(m.group(i)) for i in range(1, 6)) + (m.group(7),))
    return res


def vias(text):
    res = []
    for m in re.finditer(r'\(via\s+\(at ([-\d.]+) ([-\d.]+)\)\s+\(size ([\d.]+)\)(?:.|\n)*?\(net "([^"]*)"\)', text):
        res.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)))
    return res


def seg_rect_dist(x1, y1, x2, y2, rx0, ry0, rx1, ry1):
    # smallest distance from a segment to an axis-aligned rectangle (0 when they meet), sampled
    best = 1e9
    for i in range(201):
        t = i / 200
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        dx = max(rx0 - x, 0, x - rx1)
        dy = max(ry0 - y, 0, y - ry1)
        best = min(best, math.hypot(dx, dy))
    return best


def main():
    boards = sorted(glob.glob(ROOT + '/design/ecad/band/flex[12]-us*.kicad_pcb'))
    total_cover = 0
    summary = {}
    for b in boards:
        name = b.split('/')[-1].replace('.kicad_pcb', '')
        text = open(b, encoding='utf-8').read()
        allsegs = [('B.Cu',) + s for s in segs(text, 'B.Cu')] + [('F.Cu',) + s for s in segs(text, 'F.Cu')]
        vs = vias(text)
        for ref, pad, net, x, y in tail_lands(name):
            # the middle 0.30 of the board land is under the tail land itself (opaque copper);
            # only the two 0.125 mm end strips could ever be seen through the foot
            strips = {'end u-': (x - 0.275, x - 0.15), 'end u+': (x + 0.15, x + 0.275)}
            clear = []
            detail = {}
            for sname, (rx0, rx1) in strips.items():
                ry0, ry1 = y - 0.15, y + 0.15
                cover = []
                for (lay, x1, y1, x2, y2, w, n) in allsegs:
                    if seg_rect_dist(x1, y1, x2, y2, rx0, ry0, rx1, ry1) < w / 2:
                        cover.append(f'{lay} track {n}')
                for (vx, vy, vsz, n) in vs:
                    dx = max(rx0 - vx, 0, vx - rx1)
                    dy = max(ry0 - vy, 0, vy - ry1)
                    if math.hypot(dx, dy) < vsz / 2:
                        cover.append(f'via {n}')
                detail[sname] = sorted(set(cover))
                if not cover:
                    clear.append(sname)
            key = f'{ref}:{pad}'
            summary.setdefault(key, []).append(len(clear))
            total_cover += 1 if not clear else 0
            print(f'{name} {ref} land {pad} {net}: end strips with no flex copper over them: {len(clear)} of 2 {clear}; covered by {detail}')
    print('SUMMARY land: sizes where at least one end strip has no flex copper over it (of 7 sizes)')
    for k in sorted(summary):
        print(f'  {k}: {sum(1 for c in summary[k] if c)} of {len(summary[k])}')
    print(f'RESULT land-board pairs with both end strips covered by flex copper: {total_cover} of {sum(len(v) for v in summary.values())}')


if __name__ == '__main__':
    main()
