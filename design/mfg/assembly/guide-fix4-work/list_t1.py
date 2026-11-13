"""Run check_assembly.py unchanged (read only) in a namespace and print every T1 problem it found."""
import sys, io, contextlib
A = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/assembly")
src = open(A + '/check_assembly.py', encoding='utf-8').read()
g = {'__name__': '__main__', '__file__': A + '/check_assembly.py'}
sys.argv = [A + '/check_assembly.py'] + sys.argv[1:]
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        exec(compile(src, A + '/check_assembly.py', 'exec'), g)
except SystemExit:
    pass
print('last line of the check:', buf.getvalue().strip().split('\n')[-1])
for b in g.get('bad_t', []):
    print('T1', b)
print('T1 problems', len(g.get('bad_t', [])))
