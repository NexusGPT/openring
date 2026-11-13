# Final audit: pulls claims out of wiring-review.md by itself (paths, quoted strings, numbers) and
# prints, for each, the first evidence line that holds it (review-work logs and the cited sources),
# or NO MATCH. Usage: python3 audit.py <review.md> > audit.log
import re, sys, os, glob
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = ROOT + '/design/wiring/review-work'
text = open(sys.argv[1]).read()
ev_files = [f for f in glob.glob(W + '/**/*', recursive=True) if os.path.isfile(f) and f.endswith(('.log', '.csv', '.py', '.json', '.md', '.sh')) and 'audit' not in os.path.basename(f) and os.path.getsize(f) < 3_000_000]
src_files = [ROOT + p for p in ('/design/mfg/assembly/assembly.md', '/design/wiring/product-wiring.csv', '/design/wiring/connections.md', '/design/ecad/band/band-interface.md',
             '/design/case/case-architecture.md', '/design/wiring/screen-cable-study.md', '/design/wiring/lead-decisions.md', '/design/ecad/ring/netlist.csv', '/design/mech/thin/thin.py')]
corpus = {}
for f in ev_files + src_files:
    try:
        corpus[f] = open(f, errors='replace').read().splitlines()
    except Exception as e:
        print('cannot read', f, e)
def find(s):
    for f, lines in corpus.items():
        for i, l in enumerate(lines, 1):
            if s in l:
                return f'{f.replace(ROOT + "/", "")}:{i}: {l.strip()[:120]}'
    return None
n = 0; miss = 0
# 1. paths in backticks
for p in sorted(set(re.findall(r'`([^`]+\.(?:md|csv|log|py|kicad_pcb|kicad_pro|sh|json))`', text))):
    n += 1
    cands = [ROOT + '/' + p, ROOT + '/design/wiring/' + p, W + '/' + p.replace('review-work/', ''), ROOT + '/design/ecad/ring/' + p, ROOT + '/design/ecad/case/' + p, ROOT + '/design/ecad/ring/pcb/' + p, ROOT + '/design/ecad/case/pcb/' + p]
    hit = [c for c in cands if os.path.exists(c)]
    print(('PATH ok ' if hit else 'PATH NO MATCH ') + p + (' -> ' + hit[0].replace(ROOT + '/', '') if hit else ''))
    miss += 0 if hit else 1
# 2. quoted strings
for q in sorted(set(re.findall(r"\"([^\"\n|]{6,})\"", text))):
    n += 1
    h = find(q)
    print(('QUOTE ok ' if h else 'QUOTE NO MATCH ') + repr(q) + (' -> ' + h if h else ''))
    miss += 0 if h else 1
# 3. numbers with a decimal point or 2+ digits (skip dates and the commit)
for num in sorted(set(re.findall(r'(?<![\w.])(\d+\.\d+|\d{2,})(?![\w.])', text))):
    if num in ('2026', '13', '11', '08', '07'):
        continue
    n += 1
    h = find(num)
    print(('NUM ok ' if h else 'NUM NO MATCH ') + num + (' -> ' + h if h else ''))
    miss += 0 if h else 1
# 4. disagreements: counts stated twice
for pat in (r'(\d+) major', r'(\d+) minor', r'(\d+) notes'):
    vals = set(re.findall(pat, text))
    print('COUNT', pat, sorted(vals), 'agree' if len(vals) <= 1 else 'DISAGREE')
rows = re.findall(r'^\| (M\d|m\d|N\d) \| (major|minor|note) \|', text, re.M)
print('TABLE rows', len(rows), 'major', sum(1 for r in rows if r[1] == 'major'), 'minor', sum(1 for r in rows if r[1] == 'minor'), 'note', sum(1 for r in rows if r[1] == 'note'))
print(f'AUDIT claims checked {n}, no match {miss}')
# 5. cited line numbers that hold no searchable number: print the cited lines themselves
nl = open(ROOT + '/design/ecad/ring/netlist.csv').read().splitlines()
print('CITE ring netlist.csv line 381:', nl[380], '| line 382:', nl[381])
for f, ln in (('/design/mfg/assembly/assembly.md', (21, 55, 96, 120, 124, 201)), ('/design/wiring/connections.md', (58, 61, 65)), ('/design/ecad/band/band-interface.md', (65, 122)), ('/design/case/case-architecture.md', (205, 238)), ('/design/wiring/screen-cable-study.md', (54, 207)), ('/design/wiring/product-wiring.csv', (6, 25))):
    L = open(ROOT + f).read().splitlines()
    for k in ln:
        print(f'CITE {f}:{k}: {L[k-1][:110]}')
# 6. the review's counts against the log line that produces each (re-read, not typed)
def grab(f, pat):
    for l in open(W + '/' + f):
        m = re.search(pat, l)
        if m:
            return m.group(1)
    return None
for claim, f, pat in (('67 lines read', 'check_lines.log', r'lines read (\d+)'), ('262 end nets', 'check_lines.log', r"\('END_NET', 'pass'\): (\d+)"),
                      ('152 paths', 'check_lines.log', r"\('PATH', 'pass'\): (\d+)"), ('25 path lines', 'counts.log', r'PATH lines:\s+(\d+)'),
                      ('59 end-net lines', 'counts.log', r'END_NET lines:\s+(\d+)'), ('67 once', 'check_lines.log', r"\('ONCE', 'pass'\): (\d+)"),
                      ('28 cut lines', 'check_lines.log', r"\('CUT', 'pass'\): (\d+)"), ('0 FAIL rows', 'counts.log', r'FAIL rows: (\d+)'),
                      ('5 pin board paths', 'check_lines.log', r"\('PINBOARD_PATH', 'pass'\): (\d+)"), ('99 enumerated', 'check_cover.log', r'enumerated (\d+)'),
                      ('97 covered', 'check_cover.log', r'covered (\d+)'), ('888 parity', 'check_parity.log', r"'ok': (\d+)"), ('5 extra pads', 'check_parity.log', r"'extra': (\d+)"),
                      ('0 of 14 mating fails', 'check_mating.log', r'fails=(\d+) of 14'), ('0 of 28 pairing fails', 'check_pairing.log', r'fails=(\d+) of 28'),
                      ('21 screen-face footprints', 'ring_sides.log', r'screen face\): (\d+)'), ('0 silk items', 'case_pins_outline.log', r'silk items: (\d+)'),
                      ('4 assembly 180 hits', 'assembly-180.log', r'^(\d+):')):
    print('COUNTCHECK', claim, '->', f, grab(f, pat))
print('COUNTCHECK 17 boards with 0/0:', sum(1 for l in open(W + '/drc-summary.log') if 'Found 0 violations Found 0 unconnected items exit 0' in l))
print('COUNTCHECK j1 last line:', open(W + '/check_j1.log').read().splitlines()[-1])
print('COUNTCHECK fake1 FAIL rows:', sum(1 for l in open(W + '/fakes/fake1.log') if l.startswith('FAIL')))
