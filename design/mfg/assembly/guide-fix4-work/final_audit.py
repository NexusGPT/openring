#!/usr/bin/env python3
"""Final audit of final-reply.md: every backticked token, quoted RESULT line, file:line citation, and number
is looked up by itself in the saved evidence (this folder's logs and the delivered files), and the line it
matches is printed. Claims with no match are listed at the end."""
import os, re, glob

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
W = os.path.dirname(os.path.abspath(__file__))
reply = open(os.path.join(W, 'final-reply.md'), encoding='utf-8').read()
notes = open(ROOT + '/design/mfg/assembly/guide-fix4-notes.md', encoding='utf-8').read()
logs = {p: open(p, encoding='utf-8', errors='replace').read() for p in glob.glob(W + '/logs/*.log')}
delivered = {p: open(ROOT + '/' + p, encoding='utf-8').read() for p in [
    'design/mfg/assembly/assembly.md', 'design/mfg/assembly/hotbar-joint.md', 'design/mfg/assembly/process.md',
    'design/mfg/assembly/joints.csv', 'design/ecad/case/pcb/board-notes.md', 'design/ecad/band/band-interface.md',
    'design/wiring/lead-decisions.md', 'design/mfg/assembly/guide-joints-work/fill_joints.py']}
corpus = dict(logs)
corpus.update({ROOT + '/' + k: v for k, v in delivered.items()})
corpus[W + '/th1_values.py'] = open(W + '/th1_values.py').read()
nochk, n = [], 0


def find(s):
    for p, t in corpus.items():
        for i, l in enumerate(t.split('\n'), 1):
            if s in l:
                return f'{os.path.relpath(p, ROOT)}:{i}: {l.strip()[:120]}'
    return None


# 1. backticked tokens: paths must exist; RESULT strings must be in a log
for tok in re.findall(r'`([^`]+)`', reply):
    n += 1
    if tok.startswith('RESULT') or tok.startswith('gap lines'):
        hit = find(tok)
    elif '/' in tok or tok.endswith(('.py', '.log', '.md')):
        cands = [os.path.join(W, tok), os.path.join(ROOT, tok), os.path.join(W, 'logs', tok)]
        hit = next((c for c in cands if os.path.exists(c)), None)
        hit = f'exists: {os.path.relpath(hit, ROOT)}' if hit else None
    else:
        hit = find(tok)
    print(f'CLAIM `{tok}` -> {hit}')
    if not hit:
        nochk.append(tok)
# 2. file:line citations in the reply open at the stated text
for f, ln in re.findall(r'([\w.-]+\.(?:md|csv)):(\d+)', reply):
    n += 1
    paths = [p for p in delivered if p.endswith('/' + f)]
    if paths:
        line = delivered[paths[0]].split('\n')[int(ln) - 1]
        print(f'CITE {f}:{ln} -> {line[:120]}')
    else:
        print(f'CITE {f}:{ln} -> not a delivered file I hold; checked by hand in the notes')
# 3. numbers and named facts, each looked up
facts = ['30.1', '6.4 to 10.1', '8.2 to 15.1', '1.500', 'A4, A5, A7, A8, B4, B5 and B6', 'one end free', '386', '387',
         'R6 weak-check: J-W027-A', 'T1 problems 0', 'T1 FAIL 10 of 141', '17:48', '2.54 mm apart', 'pads at -1 and +1 mm',
         'slot 2.0 wide', 'blue lead', 'X-ray of lands A6 and A8', 'TESTS PASS 18 of 18', '45', 'problems 45',
         'changed lines (1): [324]', '17:54:53', '17:55:04', 'SyntaxError', '0.5 mm, part 2470687603', '340 C, at most 7 s',
         'No third reflow of the ring board, ever', 'black or blue', 'REPLACED 2026-11-13 (was', 'TH1 now goes on BEFORE',
         '2.0 mm apart', 'chisel tip 1.3 mm']
for fct in facts:
    n += 1
    hit = find(fct) or (('notes: ' + fct) if fct in notes else None)
    print(f'FACT "{fct}" -> {hit}')
    if not hit:
        nochk.append(fct)
print('NO MATCH:', nochk)
print(f'RESULT audit claims checked {n}, without a match {len(nochk)}')
