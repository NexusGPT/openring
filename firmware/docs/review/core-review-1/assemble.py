R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware/docs/review/")
S=R+"core-review-1/"
t=open(S+"parts.md",encoding="utf-8").read()
t=t.replace("ROWS_TABLE",open(S+"rows-table.md",encoding="utf-8").read().rstrip())
t=t.replace("MUT_TABLE",open(S+"mut-table.md",encoding="utf-8").read().rstrip())
t=t.rstrip()+"\n\nRESULT: done, 0 S1, 0 S2 and 9 S3 open; 38 of 44 mutations caught (4 real test gaps survived, 2 judged equivalent), 61 of 61 rows equal the specification.\n"
open(R+"core-review-1.md","w",encoding="utf-8").write(t)
