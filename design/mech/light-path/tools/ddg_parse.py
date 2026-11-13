"""Print title, url and snippet of each DuckDuckGo html result: ddg_parse.py <file.html>"""
import html
import re
import sys
import urllib.parse

t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
print(f"html bytes {len(t)}")
links = re.findall(r'class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)
snips = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', t, re.S)
for i, (u, ti) in enumerate(links):
    m = re.search(r"uddg=([^&]+)", u)
    url = urllib.parse.unquote(m.group(1)) if m else u
    s = snips[i] if i < len(snips) else ""
    clean = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
    print(f"[{i + 1}] {clean(ti)}\n    {url}\n    {clean(s)}")
if not links:
    print("no results parsed (blocked or empty)")
