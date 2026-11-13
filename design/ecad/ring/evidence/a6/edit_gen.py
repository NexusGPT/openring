P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/gen_sch.py")
s = open(P).read()
for old, new, n in (("('power', 'Power: nPM1300')", "('power', 'Power: nPM1304')", 1),
                    ('(rev "A5")', '(rev "A6")', 2),
                    ('architecture.md A5-draft', 'architecture.md A5-draft with 17.11 to 17.13', 2)):
    assert s.count(old) == n, (old, s.count(old))
    s = s.replace(old, new)
open(P, 'w').write(s)
