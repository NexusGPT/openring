"""Headless page reader: webtext.py <url> <out.txt> [wait_ms]. Saves the visible text of a page rendered with JavaScript,
including text inside shadow roots and frames. Dismisses a cookie banner when it finds one."""
import sys, re
from playwright.sync_api import sync_playwright
url, out = sys.argv[1], sys.argv[2]
wait = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
DEEP = """() => { const seen = []; const walk = (root) => { let t = ''; const it = document.createNodeIterator(root, NodeFilter.SHOW_ELEMENT);
  let n; while ((n = it.nextNode())) { if (n.shadowRoot) t += '\\n' + walk(n.shadowRoot); } return (root.innerText || root.textContent || '') + t; };
  return walk(document.body); }"""
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", viewport={"width": 1400, "height": 2400})
    pg = ctx.new_page()
    r = pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(4000)
    for label in ["Deny", "Decline", "Reject all", "Use necessary cookies only", "Allow all", "Accept all", "Accept", "OK"]:
        try:
            btn = pg.get_by_role("button", name=re.compile("^" + re.escape(label), re.I)).first
            if btn.count() and btn.is_visible():
                btn.click(timeout=3000); print("clicked", label); break
        except Exception as e:
            pass
    pg.wait_for_timeout(wait)
    parts = []
    for f in pg.frames:
        try:
            parts.append(f.evaluate(DEEP))
        except Exception as e:
            parts.append("")
    txt = "\n".join(parts)
    open(out, "w").write(txt)
    print("status", r.status if r else None, "final", pg.url, "frames", len(pg.frames), "chars", len(txt))
    b.close()
