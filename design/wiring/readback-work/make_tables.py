"""make_tables.py: rebuilds results/tables.md and results/verdicts.json from the raw result records (results/*.json). Verdict rules are those
frozen in board-readback.md section 0.2; nothing is typed by hand."""
import json, os, glob, collections
Wd = os.path.dirname(os.path.abspath(__file__)); R = Wd + '/results/'
J = lambda n: json.load(open(R + n))
out, V = [], []   # V: (id, board/line, figure, limit, verdict, source field)
def add(i, what, fig, lim, verdict, src): V.append(dict(id=i, what=what, figure=fig, limit=lim, verdict=verdict, source=src))
# ---------------- P1
GLOBAL_ABSENT = {'ring': ['BT1', 'DISP1', 'RT1'], 'case_main': ['BT1']}   # from logs/p1_global.log (frozen rule M4, attributed to the first board of each netlist)
boards = ['ring', 'case_main', 'case_pins'] + ['flex%d-us%d' % (f, u) for f in (1, 2) for u in range(7, 14)]
out.append('### P1 per board (Route B: Gerber + drill read-back; field names are those of the results/p1_*.json files)\n')
out.append('| board | nets compared (nets) | pads compared (pads) | shorts | opens | missing pads (missing) | refs of its netlist in no fab file | stack-model shorts/opens | route A | P1 |')
out.append('|---|---|---|---|---|---|---|---|---|---|')
for bd in boards:
    r = J('p1_%s.json' % bd)
    ga = GLOBAL_ABSENT.get(bd, [])
    ok = (r['shorts'] == 0 and r['opens'] == 0 and r['missing'] == 0 and not ga)
    ra = ''
    if 'routeA' in r:
        a = r['routeA']
        ra = 'pads %d, nets %d, joined %d, split %d, coords %d/%d' % (a['pads_compared'], a['nets'], a['groups_joined_or_differing'], a['groups_split_or_differing'], a['coord_match'], a['ipc_pad_records'])
        ok = ok and a['groups_joined_or_differing'] == 0 and a['groups_split_or_differing'] == 0 and a['coord_bad_n'] == 0
    out.append('| %s | %d | %d | %d | %d | %d %s | %s | %d/%d | %s | %s |' % (bd, r['nets'], r['pads'], r['shorts'], r['opens'], r['missing'], ('(' + ', '.join(r['missing_pads']) + ')') if r['missing_pads'] else '', ', '.join(ga) or '-', r['stack_model']['shorts'], r['stack_model']['opens'], ra or 'n/a (no .ipc356 in fab/)', 'PASS' if ok else 'FAIL'))
    add('P1.' + bd, bd, 'nets %d pads %d shorts %d opens %d missing %d absent refs %d' % (r['nets'], r['pads'], r['shorts'], r['opens'], r['missing'], len(ga)), 'all zero', 'PASS' if ok else 'FAIL', 'p1_%s.json shorts/opens/missing' % bd)
# ---------------- P2
out.append('\n### P2 broken copies of the ring board (each exported again with kicad-cli into readback-work/p2/<name>/fab)\n')
out.append('| copy | Route B shorts | Route B opens (net) | Route A joined/split | draws read | what the edit was |')
out.append('|---|---|---|---|---|---|')
P2 = {}
for m in ('control', 'resave', 'cut', 'join'):
    r = J('p1_ring_p2_%s.json' % m); P2[m] = r
    out.append('| %s | %d %s | %d %s | %d / %d | %d | %s |' % (m, r['shorts'], r['short_groups'] or '', r['opens'], r['open_nets'] or '', r['routeA']['groups_joined_or_differing'], r['routeA']['groups_split_or_differing'], r['draws_checked'], {'control': 'byte copy, no edit', 'resave': 'loaded and saved by pcbnew, no edit', 'cut': 'one LCD_SCK segment removed', 'join': 'one added segment LCD_SCK to LCD_MOSI'}[m]))
c0 = P2['control']
det_cut = P2['cut']['opens'] == 1 and P2['cut']['open_nets'] == {'LCD_SCK': 1} and P2['cut']['shorts'] == 0 and P2['cut']['missing'] == 0
det_join = P2['join']['shorts'] == 1 and P2['join']['short_groups'] == [['LCD_MOSI', 'LCD_SCK']] and P2['join']['opens'] == 0 and P2['join']['missing'] == 0
ctl_geom = all(P2[m]['shorts'] == 0 and P2[m]['opens'] == 0 and P2[m]['missing'] == 0 and P2[m]['routeA']['groups_joined_or_differing'] == 0 for m in ('control', 'resave'))
ctl_p1 = ctl_geom and not GLOBAL_ABSENT['ring']     # frozen wording: the control must pass P1; the ring's P1 includes the three refs in no fab file
add('P2.control', 'control copy (byte copy and re-saved copy)', 'shorts/opens/missing(local) 0/0/0; refs in no fab file %s' % GLOBAL_ABSENT['ring'], 'passes P1', 'PASS' if ctl_p1 else 'FAIL', 'p1_ring_p2_control.json, p1_ring_p2_resave.json')
add('P2.cut', 'cut copy', 'opens %d %s, shorts %d' % (P2['cut']['opens'], P2['cut']['open_nets'], P2['cut']['shorts']), 'exactly one open on LCD_SCK, nothing else', 'PASS' if det_cut else 'FAIL', 'p1_ring_p2_cut.json')
add('P2.join', 'joined copy', 'shorts %d %s, opens %d' % (P2['join']['shorts'], P2['join']['short_groups'], P2['join']['opens']), 'exactly one short LCD_SCK-LCD_MOSI, nothing else', 'PASS' if det_join else 'FAIL', 'p1_ring_p2_join.json')
add('P2.routeA', 'Route A on cut and join copies (expected: not detected)', 'cut joined/split %d/%d, join %d/%d' % (P2['cut']['routeA']['groups_joined_or_differing'], P2['cut']['routeA']['groups_split_or_differing'], P2['join']['routeA']['groups_joined_or_differing'], P2['join']['routeA']['groups_split_or_differing']), 'REPORT (written expectation: not detected)', 'REPORT', 'routeA fields')
# ---------------- P3
p3r, p3b, p3c = J('p3_ring.json'), J('p3_band.json'), J('p3_case.json')
out.append('\n### P3 power paths (R from the pixel mesh of the drawn copper; check = sum of rho L/(w t) on the minimum-resistance track path where the drawn-track graph reached both pads)\n')
out.append('| path | from -> to | R mesh (mohm) | R track-sum (mohm) | current | drop (mV) | limit | verdict |')
out.append('|---|---|---|---|---|---|---|---|')
def row(label, rec, cur, limit_mV=None, note='REPORT (no written limit)'):
    d = rec['drops_mV'][cur]
    out.append('| %s | %s -> %s | %.2f | %s | %s | %.2f | %s | %s |' % (label, '+'.join(rec['src']), '+'.join(rec['sink']), rec['R_mesh_mohm'], ('%.2f' % rec['R_tracksum_mohm']) if rec['R_tracksum_mohm'] is not None else 'n/a', cur, d, ('<= %g mV' % limit_mV) if limit_mV else note, ('PASS' if d <= limit_mV else 'FAIL') if limit_mV else 'REPORT'))
    return d
for rec in p3r['VBAT']:
    row('ring VBAT', rec, '235mA')
    add('P3.ring.VBAT.%s' % rec['sink'][0], 'ring VBAT to %s at 235 mA' % '+'.join(rec['sink']), '%.2f mV' % rec['drops_mV']['235mA'], 'no written limit', 'REPORT', 'p3_ring.json VBAT')
ring_vmot = p3r['VMOT'][0]
for cur in ('175mA', '80mA'):
    d_ring = ring_vmot['drops_mV'][cur]; v13 = p3b['us13']
    tot = d_ring + v13['vmot'][0]['drops_mV'][cur] + v13['gnd_both'][0]['drops_mV'][cur]
    row('ring VMOT', ring_vmot, cur, None, 'part of the 264 mV sum below')
    add('P3.VMOT.sum.%s' % cur, 'VMOT total at %s: ring VMOT %.2f + band US13 VMOT %.2f + band US13 GND (lands 6+8) %.2f' % (cur, d_ring, v13['vmot'][0]['drops_mV'][cur], v13['gnd_both'][0]['drops_mV'][cur]), '%.2f mV' % tot, '<= 264 mV (2.964 - 2.7)', 'PASS' if tot <= 264 else 'FAIL', 'p3_ring.json VMOT, p3_band.json us13')
for rec in p3r['VBUS'][:1]:
    for cur, lim in (('15mA', 970), ('100mA', 800)):
        d = row('ring VBUS', rec, cur, lim)
        add('P3.ring.VBUS.%s' % cur, 'ring VBUS land to U2 B1+B2 at %s' % cur, '%.2f mV' % d, '<= %d mV' % lim, 'PASS' if d <= lim else 'FAIL', 'p3_ring.json VBUS')
for rec in p3r['VBUS'][1:]:
    row('ring VBUS (other loads)', rec, '15mA')
for net, curs, lim in (('VDD_1V8', ['200mA'], 90), ('VDD_SD', ['100mA', '25mA'], 300)):
    okr = [r for r in p3r[net] if 'R_mesh_mohm' in r]
    far = max(okr, key=lambda r: r['R_mesh_mohm'])
    for cur in curs:
        d = row('ring %s farthest load' % net, far, cur, lim)
        add('P3.ring.%s.%s' % (net, cur), 'ring %s source to farthest pad %s at %s' % (net, '+'.join(far['sink']), cur), '%.2f mV' % d, '<= %d mV' % lim, 'PASS' if d <= lim else 'FAIL', 'p3_ring.json %s' % net)
out.append('\n#### band circuits, every size (mohm and mV; motor lines at 175 and 80 mA, cell lines at 227.5 mA)\n')
out.append('| size | VMOT mohm | VMOT mV 175 / 80 | GND lands 6+8 mohm | GND mV 175 / 80 | GND land 6 only mV 175 | cell VBAT mohm | VBAT mV | cell GND 2+7 mohm | GND mV | GND land 2 only mV |')
out.append('|---|---|---|---|---|---|---|---|---|---|---|')
for us in (7, 8, 9, 10, 11, 12, 13):
    d = p3b['us%d' % us]
    out.append('| US %d | %.2f | %.2f / %.2f | %.2f | %.2f / %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f |' % (us, d['vmot'][0]['R_mesh_mohm'], d['vmot'][0]['drops_mV']['175mA'], d['vmot'][0]['drops_mV']['80mA'], d['gnd_both'][0]['R_mesh_mohm'], d['gnd_both'][0]['drops_mV']['175mA'], d['gnd_both'][0]['drops_mV']['80mA'], d['gnd6'][0]['drops_mV']['175mA'], d['vbat'][0]['R_mesh_mohm'], d['vbat'][0]['drops_mV']['227.5mA'], d['cell_gnd_both'][0]['R_mesh_mohm'], d['cell_gnd_both'][0]['drops_mV']['227.5mA'], d['cell_gnd2'][0]['drops_mV']['227.5mA']))
    for cur in ('175mA', '80mA'):
        tot = p3r['VMOT'][0]['drops_mV'][cur] + d['vmot'][0]['drops_mV'][cur] + d['gnd_both'][0]['drops_mV'][cur]
        if us != 13:
            add('P3.VMOT.sum.us%d.%s' % (us, cur), 'VMOT total US %d at %s (ring VMOT + band VMOT + band GND)' % (us, cur), '%.2f mV' % tot, '<= 264 mV (reported per size; the judged line is US 13)', 'REPORT', 'p3_band.json')
d13 = p3b['us13']
for lab, key, sub, stated, cur in (('band US13 VMOT', 'vmot', None, 8.7, '175mA'), ('band US13 motor GND (land 6 only, the stricter)', 'gnd6', None, 12.9, '175mA'), ('band US13 cell VBAT', 'vbat', None, 11.0, '227.5mA'), ('band US13 cell GND (land 2 only, the stricter)', 'cell_gnd2', None, 12.5, '227.5mA')):
    d = d13[key][0]['drops_mV'][cur]
    add('P3.band.us13.%s' % key, lab + ' at ' + cur, '%.2f mV (stated %.1f mV)' % (d, stated), '<= %.2f mV (1.10 x stated, band-interface.md lines 132/133)' % (1.1 * stated), 'PASS' if d <= 1.1 * stated else 'FAIL', 'p3_band.json us13.%s' % key)
vm = p3c['vring_main'][0]; vp = p3c['vring_pins'][0]
tot = vm['drops_mV']['400mA'] + vp['drops_mV']['400mA']
add('P3.case.VRING', 'case VRING U5 OUT -> W1 (case_main) %.2f mV + WP1 -> P1 (case_pins) %.2f mV at 0.400 A' % (vm['drops_mV']['400mA'], vp['drops_mV']['400mA']), '%.2f mV' % tot, '<= 901 mV', 'PASS' if tot <= 901 else 'FAIL', 'p3_case.json vring_main, vring_pins')
add('P3.case.BAT', 'case BAT U2 13+14 -> W5 at 0.350 A', '%.2f mV' % p3c['bat'][0]['drops_mV']['350mA'], 'no written limit', 'REPORT', 'p3_case.json bat')
add('P3.case.GND', 'case GND U2 25 -> W6 at 0.350 A (50 um raster)', '%.2f mV' % p3c['gnd_50um'][0]['drops_mV']['350mA'], 'no written limit', 'REPORT', 'p3_case.json gnd_50um')
out.append('\nCase: VRING main %.2f mohm (%.2f mV at 0.400 A), pins board %.2f mohm (%.2f mV); BAT %.2f mohm (%.2f mV at 0.350 A); GND %.2f mohm (%.2f mV) at the 50 um raster; VRING at the 50 um raster %.2f mohm (resolution check).' % (vm['R_mesh_mohm'], vm['drops_mV']['400mA'], vp['R_mesh_mohm'], vp['drops_mV']['400mA'], p3c['bat'][0]['R_mesh_mohm'], p3c['bat'][0]['drops_mV']['350mA'], p3c['gnd_50um'][0]['R_mesh_mohm'], p3c['gnd_50um'][0]['drops_mV']['350mA'], p3c['vring_main_50um'][0]['R_mesh_mohm']))
# ---------------- P4 / P5
q = J('p4p5.json')
out.append('\n### P4 and P5 (ring)\n')
z = q['P4_1']['Z0']
add('P4.1', 'antenna feed Z0 (width %.3f mm, Hammerstad-Jensen + Wheeler, er 4.1)' % q['P4_1']['modal'], '%.2f ohm' % z, '45 to 55 ohm', 'PASS' if 45 <= z <= 55 else 'FAIL', 'p4p5.json P4_1.Z0')
c2 = q['P4_2']['min_clear_mm']
add('P4.2', 'antenna L1 clearance to other-net copper (whole line; excluding 1.0 mm at U1 ball C1: %.4f mm)' % q['P4_2']['min_clear_excl_1mm'], '%.4f mm at %s (copper of %s)' % (c2, q['P4_2']['at'], q['P4_2']['other']), '>= 0.200 mm', 'PASS' if c2 >= 0.200 else 'FAIL', 'p4p5.json P4_2.min_clear_mm')
add('P4.3', 'antenna reference: share of line pixels over L2 GND (L2 other-net copper under the line: %d px)' % q['P4_3']['other_net_px'], '%.3f percent (%d px uncovered)' % (q['P4_3']['cov_pct'], q['P4_3']['uncovered_px']), '100 percent and no other-net L2 copper', 'PASS' if (q['P4_3']['uncovered_px'] == 0 and q['P4_3']['other_net_px'] == 0) else 'FAIL', 'p4p5.json P4_3')
u = q['P4_4']; zs = [u['Zdiff_min'], u['Zdiff_median'] if 'Zdiff_median' in u else None, u['Zdiff_mode']]
import math
H, T, ER = 0.065, 0.018, 4.1
zmed = 2 * u['Z0'] * (1 - 0.48 * math.exp(-0.96 * u['gap_median'] / H))
zz = [u['Zdiff_min'], zmed, u['Zdiff_mode']]
add('P4.4', 'USB Zdiff at the min / median / modal drawn gap (%.4f / %.4f / %.3f mm), width %.3f mm' % (u['gap_min'], u['gap_median'], u['gap_mode'], u['modal_w']), '%.2f / %.2f / %.2f ohm' % tuple(zz), '81 to 99 ohm at all three (stricter reading, stated)', 'PASS' if all(81 <= x <= 99 for x in zz) else 'FAIL', 'p4p5.json P4_4')
uo = q['P4_usb_other']
add('P4.usb.other', 'USB pair (both legs) nearest other-net L1 copper', '%.4f mm (copper of %s)' % (uo[0], uo[2]), 'plan: 0.200 mm class gap (d.2 "0.200 to other copper") REPORT', 'REPORT', 'p4p5.json P4_usb_other')
add('P4.usb.ref', 'USB pair reference L2 GND coverage', '%.3f percent (%d px uncovered; %d px of other-net L2 copper under the pair)' % (q['P4_3u']['cov_pct'], q['P4_3u']['uncovered_px'], q['P4_3u']['other_px']), 'plan d.2: reference L2 solid; REPORT', 'REPORT', 'p4p5.json P4_3u')
mm = q['P4_5']['mismatch']
add('P4.5', 'USB leg mismatch (shortest paths %.3f / %.3f mm; total drawn %.3f / %.3f mm, mismatch %.3f)' % (q['P4_5']['l_dp'], q['P4_5']['l_dn'], q['P4_5']['t_dp'], q['P4_5']['t_dn'], abs(q['P4_5']['t_dp'] - q['P4_5']['t_dn'])), '%.3f mm' % mm, '<= 0.10 mm', 'PASS' if mm <= 0.10 and abs(q['P4_5']['t_dp'] - q['P4_5']['t_dn']) <= 0.10 else 'FAIL', 'p4p5.json P4_5')
add('P4.len', 'antenna line length, sum of legs', '%.3f mm' % q['P4_len']['sum'], 'plan 16.4 mm, no tolerance written', 'REPORT', 'p4p5.json P4_len')
for k, v in q['P4_per_layer'].items():
    add('P4.near.L%s' % k, 'nearest other-net copper to the antenna line on L%s' % k, '%.4f mm (copper of %s)' % (v[0], v[2]), 'REPORT', 'REPORT', 'p4p5.json P4_per_layer')
P5 = q['P5']
for n in ('XL1', 'XL2', 'XC1', 'XC2'):
    p = P5[n]; L = p['path'] if p['path'] is not None else p['total']
    add('P5.%s.len' % n, '%s length (shortest drawn path pad to pad; all drawn copper %.3f mm)' % (n, p['total']), '%.3f mm' % L, '<= %.1f mm' % p['limit'], 'PASS' if L <= p['limit'] else 'FAIL', 'p4p5.json P5.%s' % n)
lx = [P5[n]['path'] if P5[n]['path'] is not None else P5[n]['total'] for n in ('XC1', 'XC2')]
add('P5.XC.match', '|XC1 - XC2|', '%.3f mm' % abs(lx[0] - lx[1]), '<= 0.5 mm', 'PASS' if abs(lx[0] - lx[1]) <= 0.5 else 'FAIL', 'p4p5.json P5')
for n in ('XL1', 'XL2', 'XC1', 'XC2'):
    cl = P5[n]['clear']; mn = min(cl.items(), key=lambda kv: kv[1][0])
    add('P5.%s.gap' % n, '%s nearest other-net copper on its layers (%s)' % (n, '; '.join('L%s %.4f' % (k, v[0]) for k, v in cl.items())), '%.4f mm on L%s (copper of %s)' % (mn[1][0], mn[0], mn[1][2]), '>= 0.20 mm', 'PASS' if mn[1][0] >= 0.20 else 'FAIL', 'p4p5.json P5.%s.clear' % n)
out.append('| id | item | figure | limit | verdict | results field |\n|---|---|---|---|---|---|')
for v in V:
    if v['id'].startswith(('P2', 'P3.VMOT', 'P3.band', 'P3.case', 'P3.ring.VBUS', 'P3.ring.VDD', 'P4', 'P5')):
        out.append('| %s | %s | %s | %s | %s | %s |' % (v['id'], v['what'], v['figure'], v['limit'], v['verdict'], v['source']))
cnt = collections.Counter(v['verdict'] for v in V)
byp = collections.defaultdict(collections.Counter)
for v in V: byp[v['id'].split('.')[0]][v['verdict']] += 1
out.append('\nVerdict counts: %s; per pass line: %s' % (dict(cnt), {k: dict(c) for k, c in byp.items()}))
open(R + 'tables.md', 'w').write('\n'.join(out) + '\n')
json.dump(dict(verdicts=V, counts=dict(cnt), per_line={k: dict(c) for k, c in byp.items()}), open(R + 'verdicts.json', 'w'), indent=1)
print('\n'.join(out))
