"""Makes an ngspice-readable copy of a maker's PSpice model; the original file is never changed.
Changes, all mechanical: IF -> ternary_fcn, & -> &&, | -> ||, {{ }} -> { }, TABLE form (becomes pwl);  VSWITCH models become SW models (Vt = (Von+Voff)/2, Vh = |Von-Voff|/2, the same two thresholds).
Usage: python convert_pspice.py original.lib converted.lib
The converted copy is read with `set ngbehavior=ps` (ngspice's PSpice mode), which handles IF(...) and the other ABM forms.
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="latin-1").read()
count = [0]


def fix(m):
    line = m.group(0)
    params = dict((k.lower(), v) for k, v in re.findall(r"(\w+)\s*=\s*([0-9.eE+\-]+[a-zA-Z]*)", line))

    def num(s):
        s = s.strip()
        mult = {"g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "v": 1.0}
        mm = re.match(r"^([0-9.eE+\-]+?)(g|meg|k|m|u|n|v)?v?$", s.lower())
        if not mm:
            return float(s)
        return float(mm.group(1)) * mult.get(mm.group(2) or "v", 1.0)
    von, voff = num(params["von"]), num(params["voff"])
    name = re.match(r"\.model\s+(\S+)", line, re.I).group(1)
    count[0] += 1
    return ".MODEL %s SW(Ron=%s Roff=%s Vt=%g Vh=%g)" % (name, params["ron"], params["roff"], (von + voff) / 2, abs(von - voff) / 2)


out = re.sub(r"^\.model\s+\S+\s+VSWITCH.*$", fix, text, flags=re.I | re.M)


def fix_tables(t):
    """PSpice  TABLE {expr} ( (x,y) (x,y) )  becomes ngspice  TABLE {expr} = (x,y) (x,y)  (the outer parentheses go)."""
    res, i, n = [], 0, 0
    pat = re.compile(r"TABLE\s*\{")
    while True:
        m = pat.search(t, i)
        if not m:
            res.append(t[i:])
            break
        j = m.end()
        depth = 1
        while depth:
            depth += {"{": 1, "}": -1}.get(t[j], 0)
            j += 1
        expr_end = j
        k = expr_end
        while t[k] in " \t\n+":
            k += 1
        if t[k] != "(":
            res.append(t[i:expr_end])
            i = expr_end
            continue
        depth, e = 1, k + 1
        while depth:
            depth += {"(": 1, ")": -1}.get(t[e], 0)
            e += 1
        inner = t[k + 1:e - 1]
        pairs = re.findall(r"\(\s*([^(),]+)\s*,\s*([^(),]+)\s*\)", inner)
        expr = t[m.end():expr_end - 1].strip()
        # TABLE {expr} (...) becomes VALUE { pwl(expr, x1, y1, x2, y2, ...) }: the same piecewise-linear curve
        res.append(t[i:m.start()] + "VALUE { pwl(" + expr + ", " + ", ".join("%s, %s" % (a, b) for a, b in pairs) + ") }")
        i = e
        n += 1
    count[1] = n
    return "".join(res)


count.append(0)
out = fix_tables(out)
# other mechanical changes: IF(c,a,b) -> ternary_fcn(c,a,b); '&' -> '&&' and '|' -> '||' inside expressions; double braces
out = re.sub(r"\bIF\s*\(", "ternary_fcn(", out, flags=re.I)
out = out.replace("{{", "{").replace("}}", "}")
out = re.sub(r"\s+TC=0,0", "", out)   # zero temperature coefficients, no effect
out = re.sub(r"(?<![&])&(?![&])", "&&", out)
out = re.sub(r"(?<![|])\|(?![|])", "||", out)
open(dst, "w", encoding="latin-1").write(out)
print("converted %d VSWITCH models and %d TABLE expressions: %s -> %s" % (count[0], count[1], src, dst))
