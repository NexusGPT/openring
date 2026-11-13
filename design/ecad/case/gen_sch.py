#!/usr/bin/env python3
"""Generates the KiCad 10 project of the ring from netlist.csv, parts.csv and
symbols.csv (written by make_netlist.py): ring.kicad_sym, ring.kicad_sch (root),
one sub-sheet per block, ring.kicad_pro, sym-lib-table.
Format copied from schematics KiCad wrote itself (template Arduino_Nano, version 20250114)."""
import csv, os, uuid, json, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = 'case'
G = 2.54
PIN_LEN = 2.54
STUB = 2.54
NS = uuid.UUID('7c2d3d66-1e8f-4d68-ab4f-7f303d2bac21')

SHEETS = [
    ('main', 'ESP32-S3 module, light, pull-ups'),
    ('power', 'Power: BQ25895 charger, TPS63802 3.3 V, cell'),
    ('usbc', 'USB-C input'),
    ('ringlink', 'Ring link: VRING switch, ESD, spring pins, touch'),
    ('storage', 'Storage (SD 4-bit)'),
    ('test', 'Test pads'),
]
# nets that carry power into power_in pins only through a passive part or from
# outside the board: flagged as driven (explained in sch-notes.md)
PWR_FLAG_NETS = {'GND': 'power'}


def U(*parts):
    return str(uuid.uuid5(NS, '/'.join(parts)))


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def fmt(v):
    v = round(v, 4)
    return ('%.4f' % v).rstrip('0').rstrip('.') if v != int(v) else str(int(v))


def snap(v):
    return round(v / 1.27) * 1.27


FONT = '(effects (font (size 1.27 1.27)))'
FONT_HIDE = '(effects (font (size 1.27 1.27)) (hide yes))'


def read():
    net = list(csv.DictReader(open(os.path.join(HERE, 'netlist.csv'))))
    parts = list(csv.DictReader(open(os.path.join(HERE, 'parts.csv'))))
    syms = {}
    for r in csv.DictReader(open(os.path.join(HERE, 'symbols.csv'))):
        syms.setdefault(r['symbol'], []).append((r['pin_number'], r['pin_name'], r['pin_type']))
    return net, parts, syms


def sym_geom(name, pins):
    """returns dict with half width, pin positions (lib coords) and sides."""
    n = len(pins)
    pl = 5.08 if n > 2 else 2.54
    if name == 'nRF54LM20A_CAAA':
        def key(p):
            nm = p[1]
            if nm.startswith('P'):
                return (1, nm)
            return (0, nm)
        pins = sorted(pins, key=key)
    if n == 1:
        left, right = [], [pins[0]]
    elif n == 2:
        left, right = [pins[0]], [pins[1]]
    else:
        h = (n + 1) // 2
        left, right = pins[:h], pins[h:]
    rows = max(len(left), len(right))
    def tl(p):
        return 0 if p[1] in ('~', '1') else len(p[1])
    namew = max([tl(p) for p in left] + [0]) + max([tl(p) for p in right] + [0])
    hw = max(G * 2, snap((namew * 1.0 + 9) / 2 / G + 0.5) * G)
    hw = round(hw / G) * G
    top = (rows - 1) * G / 2
    top = snap(top)
    pos = {}
    for i, p in enumerate(left):
        pos[p[0]] = (-hw - pl, top - i * G, 0, 'L')
    for i, p in enumerate(right):
        pos[p[0]] = (hw + pl, top - i * G, 180, 'R')
    bt = top + G
    bb = top - (rows - 1) * G - G
    return dict(hw=hw, pos=pos, top=bt, bottom=bb, rows=rows, pl=pl)


def sym_body(name, pins, geom, libname):
    hide_names = all(p[1] in ('~', '1') for p in pins)
    out = []
    out.append('(symbol %s' % q(libname))
    if name == 'PWR_FLAG':
        out.append('(power)')
    out.append('(pin_numbers (hide %s))' % ('yes' if name in ('PWR_FLAG',) else 'no'))
    out.append('(pin_names (offset 0.508)%s)' % (' (hide yes)' if hide_names else ''))
    out.append('(exclude_from_sim no) (in_bom %s) (on_board %s)' % (
        ('no', 'no') if name == 'PWR_FLAG' else ('yes', 'yes')))
    ref = '#FLG' if name == 'PWR_FLAG' else 'X'
    out.append('(property "Reference" %s (at 0 %s 0) %s)' % (q(ref), fmt(geom['top'] + 1.27),
                                                            FONT_HIDE if name == 'PWR_FLAG' else FONT))
    out.append('(property "Value" %s (at 0 %s 0) %s)' % (q(name), fmt(geom['bottom'] - 1.27), FONT))
    out.append('(property "Footprint" "" (at 0 0 0) %s)' % FONT_HIDE)
    out.append('(property "Datasheet" "" (at 0 0 0) %s)' % FONT_HIDE)
    out.append('(property "Description" %s (at 0 0 0) %s)' % (q('ring project symbol ' + name), FONT_HIDE))
    short = libname.split(':')[-1]
    out.append('(symbol %s (rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type background))))' % (
        q(short + '_0_1'), fmt(-geom['hw']), fmt(geom['top']), fmt(geom['hw']), fmt(geom['bottom'])))
    pl = []
    for num, pname, ptype in pins:
        x, y, ang, side = geom['pos'][num]
        pl.append('(pin %s line (at %s %s %d) (length %s) (name %s %s) (number %s %s))' % (
            ptype, fmt(x), fmt(y), ang, fmt(geom['pl']), q(pname), FONT, q(num), FONT))
    out.append('(symbol %s %s)' % (q(short + '_1_1'), ' '.join(pl)))
    out.append('(embedded_fonts no))')
    return '\n'.join(out)


def main():
    net, parts, syms = read()
    syms['PWR_FLAG'] = [('1', 'pwr', 'power_out')]
    geoms = {s: sym_geom(s, p) for s, p in syms.items()}
    # symbol library
    lib = ['(kicad_symbol_lib (version 20241209) (generator "ring_gen_sch") (generator_version "10.0")']
    for s, p in syms.items():
        lib.append(sym_body(s, p, geoms[s], s))
    lib.append(')')
    open(os.path.join(HERE, 'case.kicad_sym'), 'w').write('\n'.join(lib) + '\n')
    open(os.path.join(HERE, 'sym-lib-table'), 'w').write(
        '(sym_lib_table\n  (version 7)\n  (lib (name "case")(type "KiCad")(uri "${KIPRJMOD}/case.kicad_sym")(options "")(descr "case project symbols"))\n)\n')

    pinnet = {}
    for r in net:
        pinnet[(r['reference'], r['pin_number'])] = r['net'] if r['pin_type'] != 'no_connect' else None

    root_uuid = U('root')
    sheet_uuid = {s: U('sheet', s) for s, _ in SHEETS}
    flagn = 0
    for si, (sname, stitle) in enumerate(SHEETS):
        sp = [p for p in parts if p['sheet'] == sname]
        items = [(p['reference'], p['symbol'], p) for p in sp]
        for fnet, fsheet in PWR_FLAG_NETS.items():
            if fsheet == sname:
                flagn += 1
                items.append(('#FLG%02d' % flagn, 'PWR_FLAG', {'value': 'PWR_FLAG', 'mpn': '', 'footprint': '',
                                                             'dnp': 'no', 'flagnet': fnet}))
        # size of each block
        blocks = []
        for ref, s, p in items:
            g = geoms[s]
            ll = rl = 0
            for num, pname, _ in syms[s]:
                n = p.get('flagnet') if s == 'PWR_FLAG' else pinnet.get((ref, num))
                L = (len(n) * 1.0 + 4) if n else 2
                if g['pos'][num][3] == 'L':
                    ll = max(ll, L)
                else:
                    rl = max(rl, L)
            w = ll + rl + 2 * (g['hw'] + g['pl'] + STUB) + 8
            h = (g['top'] - g['bottom']) + 9
            blocks.append((ref, s, p, w, h, ll))
        # paper choice and packing in columns
        for paper, (PW, PH) in (('A4', (297, 210)), ('A3', (420, 297)), ('A2', (594, 420)), ('A1', (841, 594))):
            x0, y0, x, y, colw, ok = 15, 30, 15, 30, 0, True
            place = []
            for ref, s, p, w, h, ll in blocks:
                if y + h > PH - 40 and y > y0:
                    x += colw; y = y0; colw = 0
                place.append((ref, s, p, x, y, w, h, ll))
                y += h; colw = max(colw, w)
            if x + colw <= PW - 10:
                break
        body = []
        labels = []
        nc = []
        wires = []
        insts = []
        for ref, s, p, x, y, w, h, ll in place:
            g = geoms[s]
            sx = snap(x + ll + STUB + g['pl'] + g['hw'] + 2)
            sy = snap(y + 4 + g['top'])
            pins_xml = []
            for num, pname, ptype in syms[s]:
                px, py, ang, side = g['pos'][num]
                ax, ay = sx + px, sy - py
                n = p.get('flagnet') if s == 'PWR_FLAG' else pinnet.get((ref, num))
                pins_xml.append('(pin %s (uuid %s))' % (q(num), q(U(sname, ref, 'pin', num))))
                if n is None:
                    nc.append('(no_connect (at %s %s) (uuid %s))' % (fmt(ax), fmt(ay), q(U(sname, ref, 'nc', num))))
                    continue
                ex = ax - STUB if side == 'L' else ax + STUB
                wires.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))' % (
                    fmt(ax), fmt(ay), fmt(ex), fmt(ey := ay), q(U(sname, ref, 'w', num))))
                ang_l = 180 if side == 'L' else 0
                just = 'right' if side == 'L' else 'left'
                labels.append('(global_label %s (shape passive) (at %s %s %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s) (property "Intersheetrefs" "${INTERSHEET_REFS}" (at %s %s 0) (effects (font (size 1.27 1.27)) (justify %s) (hide yes))))' % (
                    q(n), fmt(ex), fmt(ey), ang_l, just, q(U(sname, ref, 'l', num)), fmt(ex), fmt(ey), just))
            refv = ref
            props = []
            props.append('(property "Reference" %s (at %s %s 0) %s)' % (q(refv), fmt(sx), fmt(sy - g['top'] - 1.27),
                                                                       FONT_HIDE if s == 'PWR_FLAG' else FONT))
            props.append('(property "Value" %s (at %s %s 0) %s)' % (q(p['value']), fmt(sx), fmt(sy - g['bottom'] + 1.27), FONT))
            props.append('(property "Footprint" "" (at %s %s 0) %s)' % (fmt(sx), fmt(sy), FONT_HIDE)); props.append('(property "Footprint_plan" %s (at %s %s 0) %s)' % (q(p['footprint']), fmt(sx), fmt(sy), FONT_HIDE))
            props.append('(property "Datasheet" "" (at %s %s 0) %s)' % (fmt(sx), fmt(sy), FONT_HIDE))
            props.append('(property "Description" "" (at %s %s 0) %s)' % (fmt(sx), fmt(sy), FONT_HIDE))
            props.append('(property "MPN" %s (at %s %s 0) %s)' % (q(p['mpn']), fmt(sx), fmt(sy), FONT_HIDE))
            dnp = p.get('dnp', 'no')
            onb = 'no' if s == 'PWR_FLAG' else 'yes'
            body.append('(symbol (lib_id %s) (at %s %s 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp %s) (uuid %s) %s %s (instances (project %s (path %s (reference %s) (unit 1)))))' % (
                q('case:' + s), fmt(sx), fmt(sy), onb, onb, dnp, q(U(sname, ref)), ' '.join(props), ' '.join(pins_xml),
                q(PROJ), q('/' + root_uuid + '/' + sheet_uuid[sname]), q(refv)))
        used = sorted(set(s for _, s, *_ in place))
        libsyms = [sym_body(s, syms[s], geoms[s], 'case:' + s) for s in used]
        txt = ['(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0")',
               '(uuid %s)' % q(sheet_uuid[sname]), '(paper %s)' % q(paper),
               '(title_block (title %s) (company "") (rev "C2") (comment 1 "generated by gen_sch.py from netlist.csv"))' % q(stitle),
               '(lib_symbols', *libsyms, ')', *wires, *nc, *labels, *body, '(embedded_fonts no))']
        open(os.path.join(HERE, 'case_%s.kicad_sch' % sname), 'w').write('\n'.join(txt) + '\n')

    # root sheet
    rs = []
    for i, (sname, stitle) in enumerate(SHEETS):
        x = 20 + (i % 3) * 90
        y = 40 + (i // 3) * 45
        rs.append('(sheet (at %s %s) (size 75 30) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid %s) (property "Sheetname" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project %s (path %s (page %s)))))' % (
            fmt(x), fmt(y), q(sheet_uuid[sname]), q(stitle), fmt(x), fmt(y - 0.7116), q('case_%s.kicad_sch' % sname),
            fmt(x), fmt(y + 30.5884), q(PROJ), q('/' + root_uuid), q(str(i + 2))))
    root = ['(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0")',
            '(uuid %s)' % q(root_uuid), '(paper "A4")',
            '(title_block (title "AI ring recorder: charging case schematic") (rev "C2") (comment 1 "case-architecture.md C2; source of truth netlist.csv"))',
            '(lib_symbols)', *rs,
            '(sheet_instances (path "/" (page "1")))', '(embedded_fonts no))']
    open(os.path.join(HERE, 'case.kicad_sch'), 'w').write('\n'.join(root) + '\n')
    pro = {"meta": {"filename": "case.kicad_pro", "version": 3},
           "sheets": [[root_uuid, "Root"]] + [[sheet_uuid[s], t] for s, t in SHEETS],
           "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
           "boards": [], "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
           "text_variables": {}}
    json.dump(pro, open(os.path.join(HERE, 'case.kicad_pro'), 'w'), indent=2)
    print('sheets', len(SHEETS), 'symbols', len(syms), 'parts', len(parts))


if __name__ == '__main__':
    main()
