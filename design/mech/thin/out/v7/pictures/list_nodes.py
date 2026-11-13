import sys, importlib.util
sys.argv = ['x', (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin/out/v7/pictures")]
s = importlib.util.spec_from_file_location('r', (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin/render.py"))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
for n, c, V, T in m.load():
    print(n, c, len(T), V.min(axis=0).round(2).tolist(), V.max(axis=0).round(2).tolist())
