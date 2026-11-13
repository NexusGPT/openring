import sys
src = open(sys.argv[1]).read()
L = ["F.Cu","In1.Cu","In2.Cu","In3.Cu","In4.Cu","B.Cu"]
ps = ""; names = []
for i in range(5):
    n = f"Via[{i}-{i+1}]_200:100_um"; names.append(n)
    ps += f'    (padstack "{n}"\n      (shape (circle {L[i]} 200))\n      (shape (circle {L[i+1]} 200))\n      (attach off)\n    )\n'
marker = "  )\n  (network"
assert src.count(marker) == 1
src = src.replace(marker, ps + marker)
vl = '    (via "Via[0-5]_250:150_um")'
assert src.count(vl) == 1
src = src.replace(vl, '    (via "Via[0-5]_250:150_um" ' + " ".join(f'"{n}"' for n in names) + ")")
open(sys.argv[2], "w").write(src)
