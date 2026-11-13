"""Resolve {KEY "quote"}, {KEY pN image} and {design/path "quote"} in process-src.md to page or line; write process.md.
Placeholders RESULT_COUNTS_PLACEHOLDER and RESULT_LINE_PLACEHOLDER are replaced by the files logs/result-counts.md and logs/result-line.txt."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cites_lib import *
W = os.path.dirname(os.path.abspath(__file__))
src = open(W + '/process-src.md', encoding='utf-8').read()
log, bad = [], 0
def rep(m):
    global bad
    s = m.group('src')
    if m.group('img'):
        pg = int(m.group('pg'))
        img = IMAGES.get((s, pg))
        ok = img and os.path.isfile(os.path.join(W, img))
        log.append('IMAGE %s p%d %s %s' % (s, pg, img, 'present' if ok else 'MISSING'))
        if not ok: bad += 1
        return '(%s p.%d, drawing image, seen in WORK/%s)' % (s, pg, img)
    q = m.group('q')
    path = D + KEYS[s] if s in KEYS else ROOT + '/' + s
    hits = find(path, q) if os.path.isfile(path) else []
    if not hits:
        bad += 1
        log.append('NOTFOUND %s | %s' % (s, q))
        return '(%s ?: "%s")' % (s, q)
    log.append('FOUND %s %s | %s' % (s, ','.join(hits[:3]), q))
    lab = hits[0]
    return ('(%s %s: "%s")' % (s, lab, q)) if s in KEYS else ('(`%s%s`: "%s")' % (s, lab, q))
out = CITE.sub(rep, src)
for name, fn in [('RESULT_COUNTS_PLACEHOLDER', 'logs/result-counts.md'), ('RESULT_LINE_PLACEHOLDER', 'logs/result-line.txt')]:
    if os.path.isfile(os.path.join(W, fn)):
        out = out.replace(name, open(os.path.join(W, fn)).read().rstrip('\n'))
open(ROOT + '/design/mfg/assembly/process.md', 'w', encoding='utf-8').write(out)
open(W + '/logs/resolve.log', 'w').write('\n'.join(log) + '\nRESOLVE citations %d not found or missing image %d\n' % (len(log), bad))
print('RESOLVE citations %d not found or missing image %d' % (len(log), bad))
