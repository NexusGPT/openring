import sys, html, re
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
t = re.sub(r"(?s)<[^>]+>", "\n", t)
t = html.unescape(t)
lines = [re.sub(r"\s+", " ", l).strip() for l in t.split("\n")]
print("\n".join(l for l in lines if l))
