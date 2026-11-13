"""Final audit: pulls every number, quoted text, identifier and absolute path out of the final reply and prints the saved
evidence line each matches; recounts the counts with the exact commands; checks the last line against sch-notes.md."""
import re, os, csv, glob, subprocess, sys
D = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/")
R = D + 'ecad/ring/'
E = R + 'evidence/a6/'
reply = open(E + 'final_reply.md').read()
corpus = [E + f for f in ('check_netlist_final.log', 'erc_final.log', 'check_bom_final.log', 'render_a6.log')] + \
         sorted(glob.glob(E + 'broken/*.log')) + sorted(glob.glob(E + 'swap/*')) + \
         [R + 'sch-notes.md', R + 'open-pins.csv', R + 'netlist.csv', R + 'parts.csv', R + 'make_netlist.py', R + 'check_netlist.py',
          D + 'bom.csv', D + 'bom-notes.md', D + 'architecture.md', D + 'parts/research-npm1304.md', E + 'ti_sn74axc4t774.txt',
          E + 'slim2_cs-sdnand-20230403.txt', D + 'parts/codes_tpd4e05u06_text.log', D + 'datasheets/mic-research/im68d128b-brief.txt',
          R + 'evidence/a6/run_all_final2.log', R + 'pcb/build_board.py', R + 'pcb/board-notes.md', D + 'mech/thin/placement.csv',
          D + 'parts/nordic-ref-text/caaa_schematic.txt', D + 'parts/mcu.md', R + 'additions.csv', R + 'gen_sch.py']
corpus = [c for c in corpus if os.path.isfile(c)]
text = {c: open(c, errors='replace').read().split('\n') for c in corpus}
claims = []
for m in re.finditer(r'"([^"]+)"', reply): claims.append(('quote', m.group(1)))
for m in re.finditer(r'/Users/[^\s;,)]+', reply): claims.append(('path', m.group(0).rstrip('.')))
for m in re.finditer(r'\b[A-Z][A-Za-z0-9_\-\.]*[0-9][A-Za-z0-9_\-\.]*\b', reply):
    claims.append(('ident', m.group(0).rstrip('.')))
for m in re.finditer(r'(?<![A-Za-z0-9_\.])\d+(?:\.\d+)?(?![A-Za-z0-9_])', reply): claims.append(('number', m.group(0)))
seen = set(); nclaims = 0; unmatched = []
for kind, c in claims:
    if (kind, c) in seen: continue
    seen.add((kind, c)); nclaims += 1
    if kind == 'path':
        ok = os.path.exists(c)
        print('%-6s %-70s %s' % (kind, c[-70:], 'exists' if ok else 'MISSING'))
        if not ok: unmatched.append((kind, c))
        continue
    hit = None
    for f in corpus:
        for i, l in enumerate(text[f], 1):
            if c in l:
                hit = '%s:%d: %s' % (os.path.relpath(f, D), i, l.strip()[:90]); break
        if hit: break
    print('%-6s %-34s %s' % (kind, c[:34], hit or 'NO MATCH'))
    if not hit: unmatched.append((kind, c))
print('\n--- recounts with the exact commands ---')
def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
fails = []
def expect(name, got, want):
    st = 'ok' if str(got) == str(want) else 'DIFFERENT'
    print('%-62s got %-8s want %-8s %s' % (name, got, want, st))
    if st != 'ok': fails.append(name)
expect('ok lines in check_netlist_final.log', sh("grep -c '^ok' %scheck_netlist_final.log" % E), 39)
expect('last line of check_netlist_final.log before exit', sh("tail -n 2 %scheck_netlist_final.log | head -n 1" % E), 'RESULT PASS netlist netlist.csv')
expect('exit line of check_netlist_final.log', sh("tail -n 1 %scheck_netlist_final.log" % E), 'exit 0')
expect('ERC line', sh("grep -c 'Found 0 violations' %serc_final.log" % E), 1)
expect('ERC exit', sh("tail -n 1 %serc_final.log" % E), 'exit 0')
expect('check_bom line', sh("tail -n 2 %scheck_bom_final.log | head -n 1" % E), 'lines 78, designators 130, section-2 rows 21, section-2 part tokens 27, failures 0')
expect('check_bom exit', sh("tail -n 1 %scheck_bom_final.log" % E), 'exit 0')
for n, w in (('b1_u10_pin12_net_removed', 4), ('b2_u3_clk_direct_to_chip_net', 4), ('b3_jband_a_motor_plus_on_gnd', 2), ('b4_cp1_vbus_pad_on_vbusout', 7)):
    expect('FAIL lines %s' % n, sh("grep -c '^FAIL' %sbroken/%s.log" % (E, n)), w)
    expect('exit %s' % n, sh("tail -n 1 %sbroken/%s.log" % (E, n)), 'exit 1')
op = list(csv.DictReader(open(R + 'open-pins.csv')))
expect('open-pins.csv data rows', len(op), 105)
expect('U2 ball rows in open-pins.csv', sum(1 for r in op if r['reference'] == 'U2' and r['pin_number']), 33)
expect('BAND_SPLIT line in make_netlist.py', sh("grep -n '^BAND_SPLIT = \\[' %smake_netlist.py | cut -d: -f1" % R), 128)
expect('U10 order code in parts.csv', sh("grep '^U10,' %sparts.csv | cut -d, -f4" % R), 'SN74AXC4T774RSVR')
expect('U2 mpn in parts.csv (empty)', repr(sh("grep '^U2,' %sparts.csv | cut -d, -f4" % R)), "''")
bom = list(csv.DictReader(open(D + 'bom.csv')))
expect('bom designators', sum(len(r['reference'].split(',')) for r in bom), 130)
expect('bom references with a space or empty token', sum(1 for r in bom for t in r['reference'].split(',') if not t or ' ' in t), 0)
expect('bom CAP2 lines', sum(1 for r in bom if 'CAP2' in r['reference'].split(',')), 0)
expect('bom CAP1 lines', sum(1 for r in bom if 'CAP1' in r['reference'].split(',')), 1)
u56 = [r for r in bom if r['reference'] == 'U5,U6'][0]
expect('U5,U6 line has 67.5 dB(A)', '67.5 dB(A)' in u56['key_figures'], True)
expect('U5,U6 line has 68 dB', any('68 dB' in v for v in u56.values()), False)
u2 = [r for r in bom if r['reference'] == 'U2'][0]
expect('U2 bom order code empty and S18 in open action', (u2['maker_part_number'] == '', 'S18' in u2['open_action']), (True, True))
sys.path.insert(0, R)
import make_netlist as MK
expect('delivered pads on A', len(MK.BAND_A), 8); expect('delivered pads on B', len(MK.BAND_B), 7)
sites = [l + str(n) for l in 'ABCDEFGH' for n in range(1, 11)]
balls = {r['ball'] for r in csv.DictReader(open(D + 'parts/nrf54lm20a-csp61-pins.csv'))}
expect('named sites in 8 x 10 grid', len(sites), 80); expect('empty sites', len([s for s in sites if s not in balls]), 19)
expect('balls named inside the 8 x 10 grid', len(balls & set(sites)), 61)
expect('9*0.325+0.2 > 3.02', round(9 * 0.325 + 0.2, 3) > 3.02, True)
expect('motor swap check line', sh("grep -c 'RESULT PASS' %sswap/make_netlist_motorB.log %s../check_a6_swapB.log | tail -n 1" % (E, E)).split(':')[-1], 1)
expect('swap A6-9 pads', sh("grep 'A6-9' %s../check_a6_swapB.log | cut -c1-60" % E), 'ok   A6-9 J_BAND_A 6 pads and J_BAND_B 9 pads equal the BAND')
expect('swap ERC', sh("cat %sswap/erc_line_motorB.txt | head -n 1" % E), 'Found 0 violations')
sn_last = open(R + 'sch-notes.md').read().rstrip('\n').split('\n')[-1]
expect('reply last line equals last line of sch-notes.md', reply.rstrip('\n').split('\n')[-1] == sn_last, True)
expect('reply length under 3500', len(reply) < 3500, True)
expect('bom_notes first 70 lines unchanged', sh("head -n 70 %sbom-notes.md | cmp - %sbom-notes_before.md && echo same" % (D, E)), 'same')
# TI facts used in the notes
expect('TI orderable code in TI text', 'SN74AXC4T774RSVR' in open(E + 'ti_sn74axc4t774.txt').read(), True)
expect('storage VIH 0.625VCC in maker text', '0.625VCC' in open(E + 'slim2_cs-sdnand-20230403.txt').read(), True)
expect('research line orderable nPM1304-CAAA-R', 'nPM1304-CAAA-R' in open(D + 'parts/research-npm1304.md').read(), True)
expect('architecture 4.40 V line', '- Charge voltage 4.40 V, charge current 68 mA' in open(D + 'architecture.md').read(), True)
expect('build_board.py hardcodes 6 pads for J_BAND_A', '6 pads in one row' in open(R + 'pcb/build_board.py').read(), True)
print('\nclaims checked: %d; unmatched: %d; recount differences: %d' % (nclaims, len(unmatched), len(fails)))
for u in unmatched: print('UNMATCHED', u)
for f in fails: print('DIFFERENT', f)
