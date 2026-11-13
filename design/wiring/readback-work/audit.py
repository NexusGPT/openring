"""final audit: pulls every claim (numbers, paths, quotes, verdict counts) out of final_reply.txt and board-readback.md by itself and
matches each against the saved evidence. Numbers match when a number of the evidence, rounded to the claim's decimals, equals the claim."""
import re, os, glob, json, sys
Wd = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(Wd); ROOT = os.path.dirname(D)
ev_files = [f for f in glob.glob(Wd + '/logs/**/*', recursive=True) + glob.glob(Wd + '/results/**/*', recursive=True) + [Wd + '/hand_labels.csv', Wd + '/board-readback_prereg_frozen_copy.md'] if os.path.isfile(f) and not f.endswith(('.pyc',))]
corpus = ''
for f in ev_files:
    try: corpus += open(f, errors='ignore').read() + '\n'
    except Exception: pass
design_docs = ['/wiring/ring-board-plan.md', '/ecad/band/band-interface.md', '/ecad/motor-drive/motor-drive.md', '/sim/circuit/pass-lines.md', '/sim/circuit/sim-notes.md', '/ecad/ring/pcb/board-notes-r3.md', '/architecture.md']
docs = ''
for d in design_docs:
    docs += open(ROOT + d, errors='ignore').read() + '\n'
nums = set(); 
for m in re.finditer(r'-?\d+(?:\.\d+)?', corpus):
    nums.add(m.group(0))
fl = []
for t in nums:
    try: fl.append(float(t))
    except Exception: pass
import bisect
fl = sorted(set(fl))
def num_ok(tok):
    if tok in nums or tok.lstrip('-') in nums or ('-' + tok) in nums: return True
    d = len(tok.split('.')[1]) if '.' in tok else 0
    v = float(tok)
    tol = 0.5 * 10 ** (-d) + 1e-9
    i = bisect.bisect_left(fl, v - tol)
    return i < len(fl) and fl[i] <= v + tol
claims = 0; bad = []
for name in ('final_reply.txt', '../board-readback.md'):
    path = os.path.join(Wd, name); txt = open(path).read()
    # strip the frozen section 0 for number matching of its own text: it is the evidence of what was frozen (copy is in the corpus)
    for ln_no, ln in enumerate(txt.splitlines(), 1):
        clean = re.sub(r'/Users/[^\s)`]*', ' ', ln)
        for m in re.finditer(r'(?<![\w.])-?\d+(?:\.\d+)?(?![\w])', clean):
            tok = m.group(0)
            claims += 1
            if not num_ok(tok):
                bad.append((name, ln_no, tok, ln.strip()[:150]))
print('AUDIT numbers checked:', claims, 'unmatched:', len(bad))
for b in bad[:80]: print('AUDIT UNMATCHED', b)
# paths
pc = 0; pbad = []
for name in ('final_reply.txt', '../board-readback.md'):
    txt = open(os.path.join(Wd, name)).read()
    for m in re.finditer(r'(/Users/[^\s)`,;]+)', txt):
        p = m.group(1).rstrip('.')
        pc += 1
        if not os.path.exists(p): pbad.append((name, p))
    for m in re.finditer(r'\b((?:logs|results)/[\w./*<>-]+|[\w-]+\.(?:py|json|log|csv|md))\b', txt):
        p = m.group(1); pc += 1
        cands = [Wd + '/' + p, D + '/' + p, ROOT + '/ecad/ring/pcb/' + p, ROOT + '/ecad/band/' + p, ROOT + '/ecad/case/pcb/' + p, ROOT + '/ecad/motor-drive/' + p, ROOT + '/wiring/' + p] + glob.glob(Wd + '/**/' + os.path.basename(p), recursive=True) + glob.glob(ROOT + '/**/' + os.path.basename(p), recursive=True)
        if '*' in p or '<' in p: continue
        if not any(os.path.exists(c) for c in cands): pbad.append((name, p))
print('AUDIT paths checked:', pc, 'missing:', len(pbad))
for b in pbad[:40]: print('AUDIT MISSING PATH', b)
# quotes
qc = 0; qbad = []
for name in ('final_reply.txt', '../board-readback.md'):
    txt = open(os.path.join(Wd, name)).read()
    for m in re.finditer(r'"([^"\n]{12,200})"', txt):
        q = m.group(1); qc += 1
        if q not in corpus and q not in docs and q not in open(os.path.join(Wd, '../board-readback.md')).read().split('## 1. Results')[0]:
            qbad.append((name, q[:100]))
print('AUDIT quotes checked:', qc, 'unmatched:', len(qbad))
for b in qbad[:20]: print('AUDIT UNMATCHED QUOTE', b)
# verdict counts versus the report
v = json.load(open(Wd + '/results/verdicts.json'))
c = v['counts']; res = open(os.path.join(D, 'board-readback.md')).read().strip().splitlines()[-1]
m = re.search(r'by item (\d+) met, (\d+) failed, (\d+) reported', res)
print('AUDIT RESULT line counts', m.groups() if m else None, 'verdicts.json', c['PASS'], c['FAIL'], c['REPORT'], 'MATCH' if m and tuple(map(int, m.groups())) == (c['PASS'], c['FAIL'], c['REPORT']) else 'MISMATCH')
pl = v['per_line']
lines_met = [k for k in ('P1', 'P2', 'P3', 'P4', 'P5') if pl[k].get('FAIL', 0) == 0]
print('AUDIT pass lines with no FAIL item:', lines_met, 'RESULT line says met (P3):', 'P3' in res)
# disagreement check between reply and report: same figures
rep = open(os.path.join(D, 'board-readback.md')).read(); rep_reply = open(os.path.join(Wd, 'final_reply.txt')).read()
for key in ('1 of 5 pass lines met (P3) and 4 failed (P1, P2, P4, P5)', '28 met, 18 failed, 25 reported only'):
    print('AUDIT same statement in reply and report:', key, key in rep and key in rep_reply)
print('AUDIT done: claims checked numbers %d paths %d quotes %d' % (claims, pc, qc))
