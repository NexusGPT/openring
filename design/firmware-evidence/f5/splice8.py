import sys
fw, new81, new87 = sys.argv[1:4]
s = open(fw, encoding="utf-8").read()
a = s.index("### 8.1 nPM1300 settings")
b = s.index("### 8.6 Pads on the inside")
c = s.index("## 9. Time keeping")
n81 = open(new81, encoding="utf-8").read()
n87 = open(new87, encoding="utf-8").read()
out = s[:a] + n81 + s[b:c] + n87 + s[c:]
open(fw, "w", encoding="utf-8").write(out)
print("replaced", b - a, "chars of 8.1 to 8.5 by", len(n81), "; inserted 8.7 of", len(n87))
