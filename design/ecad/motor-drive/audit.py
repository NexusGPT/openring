"""Audit of motor-drive.md (and the final reply if given): every number, every budget key,
every cited path, every quoted present text of section 2.8, and dash style.
Usage: python -I audit.py <motor-drive.md> [<reply.txt>]"""
import re, sys, os

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
MD = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/motor-drive")
docs = [open(a, encoding='utf-8').read() for a in sys.argv[1:]]
names = sys.argv[1:]
budget = open(os.path.join(MD, 'budget.log'), encoding='utf-8').read()

corpus_files = [
    'design/datasheets/npm1304_datasheet_v1_0.txt', 'design/architecture.md', 'design/firmware.md',
    'design/bom.csv', 'design/ecad/ring/make_netlist.py', 'design/ecad/ring/additions.csv',
    'design/parts/slim-2.md', 'design/parts/slim.md', 'design/parts/ui.md',
    'design/ecad/ring/pcb/board-notes.md', 'design/datasheets/p3_sgm38046.txt',
]
for f in sorted(os.listdir(MD)):
    if (f.startswith('src_') or f.startswith('columns_') or f.startswith('fetch_') or f.startswith('search_')) and f.endswith(('.txt', '.log')):
        corpus_files.append(os.path.relpath(os.path.join(MD, f), ROOT))
corpus = {}
for f in corpus_files:
    corpus[f] = open(os.path.join(ROOT, f), encoding='utf-8', errors='replace').read()

def norm(n):
    return n.replace(',', '')

bad = 0
checked = 0
LINE_NUMS = {'62', '95', '96', '134', '135', '266', '275', '279', '285', '308', '309', '310', '311', '312', '313', '314', '315', '342',
             '44', '45', '46', '62', '63', '465', '595', '596', '597', '695', '697', '798', '703', '27', '255', '40', '70', '72', '78', '88', '89', '90', '91', '101'}
# 1. budget keys
for name, doc in zip(names, docs):
    for blk in re.findall(r'\[budget ([^\]]+)\]', doc):
        for key in re.split(r',\s*', blk):
            key = key.strip()
            if key.startswith('@'):
                continue  # short form '@3.7' continues the previous key
            base = key.split(' ')[0].rstrip(':;')
            if not re.match(r'^[A-Z][A-Z0-9_]+(@[0-9.]+(ms)?|@\.\.\.|\.\.\.)?$', base):
                print(f'SKIP {name}: prose token {base!r} in a budget citation')
                continue
            checked += 1
            if base.endswith('...'):
                stem = base[:-3]
                ok = stem in budget
            else:
                ok = (base + ' =') in budget
            print(f'KEY {name}: {base} -> {"found" if ok else "MISSING"}')
            bad += 0 if ok else 1
# 1b. value of each cited key appears on the same line of the doc
vals = {}
for bl in budget.split('\n'):
    if ' = ' in bl:
        k, rest = bl.split(' = ', 1)
        vals[k] = rest.split(' ')[0]
for name, doc in zip(names, docs):
    for line in doc.split('\n'):
        prev = None
        for blk in re.findall(r'\[budget ([^\]]+)\]', line):
            for key in re.split(r',\s*', blk):
                tok = key.strip().split(' ')[0].rstrip(':;')
                if tok.startswith('@') and prev:
                    tok = prev.split('@')[0] + tok
                if tok in vals:
                    prev = tok
                    v = vals[tok]
                    checked += 1
                    ok = v in line.replace(',', '') or v in line
                    print(f'VAL {tok} = {v} -> {"on the line" if ok else "NOT ON THE LINE"}')
                    bad += 0 if ok else 1
# 2. numbers
num_re = re.compile(r'(?<![A-Za-z0-9_.])(-?\d[\d,]*\.?\d*)')
for name, doc in zip(names, docs):
    for n in sorted(set(num_re.findall(doc)), key=lambda s: float(norm(s).rstrip('.') or 0)):
        n2 = norm(n).rstrip('.')
        if n2 in ('', '-'):
            continue
        checked += 1
        where = None
        pat = re.compile(r'(?<![\d.])' + re.escape(n2) + r'(?![\d])')
        if pat.search(budget.replace(',', '')):
            where = 'budget.log'
        else:
            for f, text in corpus.items():
                if pat.search(text.replace(',', '')):
                    where = f
                    break
        if where is None and n2 in LINE_NUMS:
            where = 'a line citation checked in part 4'
        if where is None:
            # numbers inside the doc's own file names, section numbers and pattern names are listed for review
            print(f'NUM {name}: {n} -> NOT FOUND in budget.log or sources')
            bad += 1
        else:
            print(f'NUM {name}: {n} -> {where}')
# 3. paths
for name, doc in zip(names, docs):
    for pth in sorted(set(re.findall(r'`((?:design/)[^`\s]+)`', doc))):
        checked += 1
        ok = os.path.exists(os.path.join(ROOT, pth)) or ('*' in pth and any(x.startswith(os.path.basename(pth).split('*')[0]) for x in os.listdir(os.path.join(ROOT, os.path.dirname(pth))))) or any(os.path.exists(os.path.join(ROOT, os.path.dirname(pth), x)) and x.startswith(os.path.basename(pth).replace('*', '')) for x in os.listdir(os.path.join(ROOT, os.path.dirname(pth))) if '*' in pth)
        print(f'PATH {name}: {pth} -> {"exists" if ok else "MISSING"}')
        bad += 0 if ok else 1
    for pth in sorted(set(re.findall(r'`([A-Za-z0-9_.*-]+\.(?:log|txt|png|py|pdf|csv|md))`', doc))):
        checked += 1
        cands = [os.path.join(MD, pth), os.path.join(ROOT, 'design/datasheets', pth), os.path.join(ROOT, 'design/ecad/ring', pth),
                 os.path.join(ROOT, 'design', pth), os.path.join(ROOT, 'design/parts', pth)]
        ok = any(os.path.exists(c) for c in cands)
        if '*' in pth:
            pre = pth.split('*')[0]
            ok = any(x.startswith(pre) for d in [MD, os.path.join(ROOT, 'design/datasheets')] for x in os.listdir(d))
        print(f'FILE {name}: {pth} -> {"exists" if ok else "MISSING"}')
        bad += 0 if ok else 1
# 4. quoted present texts of section 2.8 on their cited lines
doc = docs[0]
checks = [
    ('design/ecad/ring/make_netlist.py', 135, "('VDD_3V0', 'MOT+', 'A'),"),
    ('design/ecad/ring/make_netlist.py', 134, "('MOTOR_DRV', 'MOT-', 'A'),"),
    ('design/ecad/ring/make_netlist.py', 308, "part('M1', 'MOTOR', 'VC0720B088L', 'VC0720B088L', 'ring:FPC_TAIL_2', BD,"),
    ('design/ecad/ring/make_netlist.py', 309, "{'+': 'VDD_3V0', '-': 'MOTOR_DRV'})"),
    ('design/ecad/ring/make_netlist.py', 310, "part('D1', 'NSR0230P2',"),
    ('design/ecad/ring/make_netlist.py', 311, "{'K': 'VDD_3V0', 'A': 'MOTOR_DRV'})"),
    ('design/ecad/ring/make_netlist.py', 312, "part('Q1', 'DMN2450UFB4',"),
    ('design/ecad/ring/make_netlist.py', 313, "{'G': 'MOTOR_G', 'S': 'GND', 'D': 'MOTOR_DRV'})"),
    ('design/ecad/ring/make_netlist.py', 314, "two('R61', 'R', '100R', '', 'ring:R_0201', K, 'MOTOR', 'MOTOR_G')"),
    ('design/ecad/ring/make_netlist.py', 315, "two('R62', 'R', '100k', '', 'ring:R_0201', K, 'MOTOR_G', 'GND')"),
    ('design/ecad/ring/make_netlist.py', 342, "('R61', 'W6 gate series resistor 100 ohm'), ('R62', 'W6 gate pull-down 100 kohm'),"),
    ('design/ecad/ring/make_netlist.py', 275, "'PVIN': 'VBAT'"),
    ('design/ecad/ring/additions.csv', 7, 'R61,added,W6 gate series resistor 100 ohm'),
    ('design/ecad/ring/additions.csv', 8, 'R62,added,W6 gate pull-down 100 kohm'),
    ('design/bom.csv', 45, 'Motor switch,Q1,1,"N-channel MOSFET, 1.8 V gate drive, switches the motor from VDD_3V0 at full duty (architecture 17.4)",Diodes Inc.,DMN2450UFB4,'),
    ('design/bom.csv', 46, 'Motor diode,D1,1,flyback Schottky diode across the motor,onsemi,NSR0230P2T5G,'),
    ('design/bom.csv', 44, 'S21: the electronics designer must recheck the motor switch Q1 and the 3.0 V rail for 175 mA at start (they were sized for 85 mA)'),
    ('design/bom.csv', 62, 'W6 gate series resistor 100 ohm'),
    ('design/bom.csv', 63, 'W6 gate pull-down 100 kohm'),
    ('design/firmware.md', 266, 'It runs at full duty from the 3.0 V rail (VDD_3V0) through Q1 (architecture 17.4): a pulse in the table is the motor on at 3.0 V, with no PWM.'),
    ('design/firmware.md', 279, 'A pulse draws below 80 mA while the motor runs and up to 175 mA at its start, from the cell through the 3.0 V rail:'),
    ('design/firmware.md', 62, 'the motor runs at full duty (on or off), so patterns in ms need no PWM (architecture 17.4)'),
    ('design/firmware.md', 798, 'jig accelerometer sees vibration; battery current rises by 30 mA or more during the pulse'),
    ('design/firmware.md', 95, '3.45 V'), ('design/firmware.md', 96, '3.30 V'),
    ('design/firmware.md', 695, 'LDSW1 (VDD_MIC)'), ('design/firmware.md', 697, 'LDSW2 (VDD_SD)'),
    ('design/architecture.md', 285, '| W6 | Motor |'), ('design/architecture.md', 595, '- Drive: unchanged wiring W6.'),
    ('design/architecture.md', 596, '- Q1 (DMN2450UFB4)'), ('design/architecture.md', 597, '- D1 (NSR0230P2T5G'),
    ('design/architecture.md', 40, 'TX 5.0 mA'), ('design/architecture.md', 70, '| VDD_MIC |'), ('design/architecture.md', 72, '| VDD_SD |'),
    ('design/architecture.md', 78, 'stops discharge at 3.1 V'), ('design/architecture.md', 88, '| Microphones |'),
    ('design/architecture.md', 89, '| Main chip | 3.0 mA at 1.8 V'), ('design/architecture.md', 90, '0.3 mA at 3.0 V'),
    ('design/architecture.md', 91, '| Recording light | 1.5 mA'), ('design/architecture.md', 101, 'Screen on, full white, full brightness'),
    ('design/architecture.md', 465, 'Recording about 4.0 mA'),
    ('design/ecad/ring/pcb/board-notes.md', 27, '72 percent'),
    ('design/firmware.md', 703, 'dischg-limit-microamp'),
    ('design/ecad/motor-drive/src_slim_ineed-c0620bldcl27-spec.txt', 255, 'Response Time'),
]
for f, ln, txt in checks:
    checked += 1
    lines = open(os.path.join(ROOT, f), encoding='utf-8', errors='replace').read().split('\n')
    got = lines[ln - 1] if ln <= len(lines) else ''
    ok = txt in got
    print(f'LINE {f}:{ln} -> {"match" if ok else "NO MATCH: " + got[:120]}')
    bad += 0 if ok else 1
# 5. style: no em or en dashes
for name, d in zip(names, docs):
    checked += 1
    n = d.count('—') + d.count('–')
    print(f'DASH {name}: {n} em or en dashes')
    bad += 1 if n else 0
# 6. last line
checked += 1
last = docs[0].rstrip('\n').split('\n')[-1]
print('LASTLINE', 'ok' if last.startswith('RESULT: ') else 'BAD', last[:80])
bad += 0 if last.startswith('RESULT: ') else 1
for name, d in zip(names, docs):
    print(f'CHARS {name}: {len(d)}')
print(f'CHECKED {checked} claims, {bad} without a match')
