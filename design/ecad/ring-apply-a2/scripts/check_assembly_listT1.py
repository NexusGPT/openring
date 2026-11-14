"""Mechanical check of design/mfg/assembly/assembly.md.

Run: design/.venv/bin/python -I design/mfg/assembly/check_assembly.py [path/to/assembly.md] [--joints FILE] [--wiring FILE]
Prints one line per check and ends with `RESULT PASS` or `RESULT FAIL <what>`. Exit 0 on pass, 1 on fail.

Checks:
 (a) every row of design/mech/thin/placement.csv (by its reference, or by its part name when the row has no
     reference) and every reference of design/bom.csv is named in at least one step of section 2;
 (b) the step numbers run 1, 2, 3, ... with no gap and no repeat;
 (c) every step has its five fields: Join, Locate, Before, Check, After;
 (d) every step cites a file and line (path:line) or carries [PROPOSED];
 (e) every path:line citation in the whole document opens: the file exists and has that line (the cited
     text is printed, so a reader can see what each citation points at);
 (f) no "as appropriate", "to be defined", "TBD" and no em or en dash in the document;
 (g) the last line starts with "RESULT:";
 (h) design version 7 (architecture 17.30): no sentence of the document names a part or feature removed in v7
     (LED1, R41, Q2, LG1, LP1, KPG-1005, light guide, light plug, light pipe, print window, recording light,
     0.50 hole, T-LIGHT, nub, rectangular) unless the same sentence says "removed in v7"; so a step such as
     "light guide fitted" or "light plug placed" fails. Placement rows of the removed parts (LED1, LG1, LP1) are
     not required by (a): the inside model v7 drops them. A sentence that names such a term and says "removed in
     v7" but also says the part is fitted, placed, bonded, soldered, mounted, glued, inserted or installed fails
     too (a part removed in v7 is not fitted), unless the sentence is negated ("not", "never", "no", "nor") or is
     history ("until v6", "History:");
 (i) citations of design/firmware.md are by section and name, never by line (the file grows): the form is
     `design/firmware.md section 9.3, name T-SIGN`; a `design/firmware.md:NNN` citation fails; the cited section
     must exist in firmware.md and must hold the cited name (the matching line is printed);
 (j) order: a step's Before field says "step N passed" only for N lower than the step itself; every row of the
     section 1 table names its reference(s) in the step its Step column gives;
 (l) T1 (review 4 fault I3, c): a citation `file:N` must find on line N what its sentence names.
     .csv tables (not line 1, their header): a designator (C83, SW1), a part name in backticks, a net (VBUS) or a part model named in the
     citation's sentence or table row must be on the cited row (designators and part names in its key cells: ref, reference, part, item,
     net, name, *_ref; nets and models anywhere on the line); the item of the sentence is the text since the previous citation or the last
     "), "; citations joined by "; ", ", ", " to " or " and " share the text before the group; the text after a citation (60 characters)
     is read for a label that follows it; the end line of a range "a to b" is read against the group's tokens and the rest of the
     sentence; a sentence that names nothing is read against the 250 characters before it. Finding ids (F6, K15, W12) are no designators.
     Prose files: only band-interface.md, process.md and hotbar-joint.md (PROSE_FILES: no false alarm on the guide of 2026-11-13) are read; a
     token named in the citation's own item (no context, no range) or a content word of the item (5 letters or more, stop words left out)
     must be on the cited line. The other prose files (architecture.md, thin-notes.md, datasheets ...) are not read: 208 of 361 prose
     citations of the guide name a token that is not on the cited line, and 35 still do after the shared-word test, mostly right citations
     of tables of numbers (checks-harden-work/assembly/exp-md-too.log, exp-md-union.log);
 (m) P1 (review 4 fault I3, a): the facts of the guide that joints.csv states are read from joints.csv: the step and pass that give the
     15 ribbon lands their paste, the lands per group (J_BAND_A, J_BAND_B), and "on the solder layer that step S put on the N lands";
     the guide contradicts the table (the lands get no paste, bare lands, other counts, other step) fails;
 (n) L1 (review 4 fault I3, b): the facts "which land gets which tab, motor lead, charging disc" of steps 7, 8, 9 are compared with
     design/wiring/product-wiring.csv (the carrier lines of kind tab, lead M1 and the copper lines to CP1 to CP4) and with the
     orientation text of joints.csv: tab P+ on land 1 (VBAT), the order of the lands, the motor lands and tail lands, disc to land;
     a form the check cannot find in the step is itself a failure (reworded text must be put back into the form or the rule changed).
 (k) the charging pads: every "CPn (`pad_X`)" pair and every "order A, B, C, D" list of pad names in the document
     equals the pad rows of design/mech/thin/placement.csv (reference to part; order by angle).
"""
import csv
import os
import re
import sys

HERE = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/assembly")  # ring-apply-a2 copy: lists every T1 failure
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_ARGS = sys.argv[1:]
JOINTS = os.path.join(HERE, "joints.csv")
WIRING = os.path.join(REPO, "design", "wiring", "product-wiring.csv")
for _flag, _name in (("--joints", "JOINTS"), ("--wiring", "WIRING")):
    if _flag in _ARGS:
        _i = _ARGS.index(_flag)
        globals()[_name] = os.path.abspath(_ARGS[_i + 1])
        del _ARGS[_i:_i + 2]
DOC = _ARGS[0] if _ARGS else os.path.join(HERE, "assembly.md")
PLACEMENT = os.path.join(REPO, "design", "mech", "thin", "placement.csv")
BOM = os.path.join(REPO, "design", "bom.csv")
FIELDS = ["Join", "Locate", "Before", "Check", "After"]

fails = []


def line(tag, ok, text):
    print(f"{tag} {'PASS' if ok else 'FAIL'} {text}")
    if not ok:
        fails.append(tag)


doc = open(DOC, encoding="utf-8").read()
doc_lines = doc.splitlines()

# Section 2 and its steps
m = re.search(r"^## 2\. .*?$(.*?)^## 3\. ", doc, flags=re.S | re.M)
sec2 = m.group(1) if m else ""
line("S0", bool(sec2), "section 2 found" if sec2 else "section 2 (between '## 2.' and '## 3.') not found")
parts = re.split(r"^### Step (\d+)\. ", sec2, flags=re.M)
steps = []  # (number, text)
for i in range(1, len(parts) - 1, 2):
    steps.append((int(parts[i]), parts[i + 1]))
print(f"INFO steps found: {len(steps)}")

# (b) continuity
nums = [n for n, _ in steps]
expected = list(range(1, len(nums) + 1))
line("B1", nums == expected and len(nums) > 0,
     f"step numbers continuous 1..{len(nums)}" if nums == expected else f"step numbers {nums} differ from {expected}")

# (c) five fields per step
missing = []
for n, t in steps:
    for f in FIELDS:
        if not re.search(r"^- \*\*" + f + r":\*\* \S", t, flags=re.M):
            missing.append(f"step {n} lacks {f}")
line("C1", not missing, "every step has Join, Locate, Before, Check, After" if not missing else "; ".join(missing))

# (d) each step cites a file:line or carries [PROPOSED]
CITE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|csv|txt|py)):(\d+)`")
FWCITE = re.compile(r"`design/firmware\.md section (\d+(?:\.\d+)*), name ([^`]+)`")
nocite = [n for n, t in steps if not CITE.search(t) and not FWCITE.search(t) and "[PROPOSED" not in t]
line("D1", not nocite, "every step cites path:line, a firmware section and name, or [PROPOSED]" if not nocite else f"steps without citation: {nocite}")

# (a) coverage
steptext = "\n".join(t for _, t in steps)


def named(token):
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])", steptext) is not None


REMOVED_V7 = {"LED1", "LG1", "LP1"}
rows = list(csv.DictReader(open(PLACEMENT, encoding="utf-8")))
skipped = [r["reference"] for r in rows if r["reference"].strip() in REMOVED_V7]
if skipped:
    print(f"INFO placement rows of parts removed in v7, not required: {', '.join(skipped)}")
rows = [r for r in rows if r["reference"].strip() not in REMOVED_V7]
miss_p = []
for r in rows:
    tok = r["reference"].strip() or r["part"].strip()
    if not named(tok):
        miss_p.append(f"{r['part']}({tok})")
line("A1", not miss_p, f"all {len(rows)} placement.csv rows named in a step" if not miss_p else "placement rows not in any step: " + ", ".join(miss_p))

refs = []
for r in csv.DictReader(open(BOM, encoding="utf-8")):
    for x in r["reference"].split(","):
        if x.strip():
            refs.append(x.strip())
miss_b = [x for x in refs if not named(x)]
line("A2", not miss_b, f"all {len(refs)} bom.csv references named in a step" if not miss_b else "bom references not in any step: " + ", ".join(miss_b))

# (e) citations open
bad = []
cites = sorted(set(CITE.findall(doc)), key=lambda c: (c[0], int(c[1])))
for path, ln in cites:
    p = os.path.join(REPO, path)
    if not os.path.isfile(p):
        bad.append(f"{path}:{ln} (no file)")
        continue
    flines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    k = int(ln)
    if k < 1 or k > len(flines):
        bad.append(f"{path}:{ln} (file has {len(flines)} lines)")
        continue
    print(f"CITE {path}:{ln} | {flines[k - 1].strip()[:150]}")
line("E1", not bad, f"all {len(cites)} distinct path:line citations open" if not bad else "citations that do not open: " + "; ".join(bad))

# (f) banned phrases and dashes
banned = []
for i, l in enumerate(doc_lines, 1):
    low = l.lower()
    for b in ("as appropriate", "to be defined", "tbd"):
        if re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", low):
            banned.append(f"line {i}: '{b}'")
    if "—" in l or "–" in l:
        banned.append(f"line {i}: dash")
line("F1", not banned, "no banned phrase and no em or en dash" if not banned else "; ".join(banned))

# (h) parts and features removed in v7 appear only in sentences that say "removed in v7"
REMOVED_TERMS = ["LED1", "R41", "Q2", "LG1", "LP1", "KPG-1005", "light guide", "light plug", "light pipe",
                 "print window", "recording light", "0.50 hole", "T-LIGHT", "nub", "rectangular"]
bad_h = []
for i, l in enumerate(doc_lines, 1):
    for s in re.split(r"(?<=[.!?])\s+", l):
        if "removed in v7" in s.lower():
            hit = [t for t in REMOVED_TERMS if re.search(r"(?<![A-Za-z0-9_-])" + re.escape(t) + r"(?![A-Za-z0-9])", s, flags=re.I)]
            neg = re.search(r"\b(not|never|no|nor)\b", s, flags=re.I) or "until v6" in s.lower() or "History:" in s
            act = re.search(r"\b(fitted|fit|fits|placed|place|bonded|soldered|mounted|glued|inserted|installed|plugged)\b", s, flags=re.I)
            if hit and act and not neg:
                bad_h.append(f"line {i}: '{hit[0]}' is fitted in a sentence that says removed in v7: {s.strip()[:90]}")
            continue
        for term in REMOVED_TERMS:
            if re.search(r"(?<![A-Za-z0-9_-])" + re.escape(term) + r"(?![A-Za-z0-9])", s, flags=re.I):
                bad_h.append(f"line {i}: '{term}' in: {s.strip()[:90]}")
line("H1", not bad_h, "no part or feature removed in v7 is named outside a 'removed in v7' sentence" if not bad_h else "; ".join(bad_h))

# (i) firmware.md is cited by section and name
FW = os.path.join(REPO, "design", "firmware.md")
fw_lines = open(FW, encoding="utf-8", errors="replace").read().splitlines()
heads = []  # (line index, level, number)
for k, l in enumerate(fw_lines):
    hm = re.match(r"^(#{2,4}) (\d+(?:\.\d+)*)\.? ", l)
    if hm:
        heads.append((k, len(hm.group(1)), hm.group(2)))


def fw_section(num):
    for j, (k, lev, n) in enumerate(heads):
        if n == num:
            end = len(fw_lines)
            for k2, lev2, _ in heads[j + 1:]:
                if lev2 <= lev:
                    end = k2
                    break
            return k, end
    return None


bad_i = []
byline = re.findall(r"design/firmware\.md:\d+", doc)
for b in sorted(set(byline)):
    bad_i.append(f"{b} (cite firmware.md by section and name)")
fwc = sorted(set(FWCITE.findall(doc)), key=lambda c: (c[0], c[1]))
for num, name in fwc:
    sec = fw_section(num)
    if sec is None:
        bad_i.append(f"section {num} not found in firmware.md")
        continue
    hit = [k for k in range(sec[0], sec[1]) if name in fw_lines[k]]
    if not hit:
        bad_i.append(f"section {num} holds no '{name}'")
        continue
    print(f"FWCITE section {num}, name {name} | {fw_lines[hit[0]].strip()[:110]}")
line("I1", not bad_i, f"all {len(fwc)} firmware citations (section and name) hold their name, none by line" if not bad_i else "; ".join(bad_i))

# (j) order
bad_j = []
for n, t in steps:
    bm = re.search(r"^- \*\*Before:\*\* (.*)$", t, flags=re.M)
    if not bm:
        continue
    for pm in re.finditer(r"[Ss]teps? ((?:\d+(?:, | to | and )?)+) passed", bm.group(1)):
        nums_ = [int(x) for x in re.findall(r"\d+", pm.group(1))]
        if any(x >= n for x in nums_):
            bad_j.append(f"step {n} Before says step {max(nums_)} passed")
sec1 = re.search(r"^## 1\. .*?$(.*?)^## 2\. ", doc, flags=re.S | re.M)
stepmap = dict(steps)
if sec1:
    for row in sec1.group(1).splitlines():
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[4].isdigit():
            for tok in re.findall(r"(?<![A-Za-z0-9_])[A-Z]{1,4}\d+(?![A-Za-z0-9_])", cells[1]):
                st = int(cells[4])
                if st not in stepmap or not re.search(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])", stepmap[st]):
                    bad_j.append(f"section 1 gives step {st} for {tok}, and step {st} does not name it")
line("J1", not bad_j, "every Before field names only lower steps as passed; every section 1 row is named in its step" if not bad_j else "; ".join(bad_j))

# (k) charging pads
pad_rows = [r for r in rows if r["part"].startswith("pad_")]
pad_ref = {r["reference"].strip(): r["part"][4:] for r in pad_rows}
pad_order = [r["part"][4:] for r in sorted(pad_rows, key=lambda r: float(r["angle_deg"]))]
bad_k = []
pairs = re.findall(r"\b(CP\d) \(`pad_([A-Za-z+-]+)`\)", doc)
for ref, nm in pairs:
    if pad_ref.get(ref) != nm:
        bad_k.append(f"{ref} is pad_{pad_ref.get(ref)} in placement.csv, the document says pad_{nm}")
lists = re.findall(r"order ((?:VBUS|D-|D\+|GND)(?:, (?:VBUS|D-|D\+|GND)){1,3})", doc)
for lst in lists:
    if lst.split(", ") != pad_order:
        bad_k.append(f"pad order '{lst}' differs from placement.csv by angle {', '.join(pad_order)}")
line("K1", not bad_k and bool(pairs) and bool(lists), f"{len(pairs)} CPn pairs and {len(lists)} pad order lists agree with placement.csv ({', '.join(pad_order)})" if not bad_k and pairs and lists else ("; ".join(bad_k) or "no pad pair or order list found"))

# (l) T1: a citation file:N finds, on line N, the designator, net or part its sentence names (review 4 fault I3 c; the 45 stale bom.csv:N)
# Token forms (data): name, regex (the group 1 or the whole match is the token). A token counts only as a whole word.
TOKEN_FORMS = [
    ("designator", r"(?<![A-Za-z0-9_-])([A-Z]{1,4}\d{1,3})(?![A-Za-z0-9_])"),
    ("part model", r"(?<![A-Za-z0-9_-])((?=[A-Za-z0-9-]*[A-Z])(?=[A-Za-z0-9-]*\d)[A-Za-z0-9][A-Za-z0-9-]{5,})(?![A-Za-z0-9_-])"),
]
# words that look like a designator but are not one: change ids, open items, review ids, ring sizes, step ids, units and standards
NOT_DESIGNATOR_BEFORE = re.compile(r"(?:change|changes|review|item|items|open item|rule|rules|lead|leads|step|steps|US|model|v|version)\s*$", re.I)
NOT_TOKENS = {"AWG30", "AWG32", "SAC305", "ENIG", "ENEPIG"}
NET_NAMES = set()
for _nl in ("design/ecad/ring/netlist.csv", "design/ecad/case/netlist.csv"):
    try:
        for _r in csv.DictReader(open(os.path.join(REPO, _nl), encoding="utf-8", newline="")):
            if len(_r.get("net", "")) >= 3 and _r["net"] not in NOT_TOKENS:
                NET_NAMES.add(_r["net"])
    except OSError:
        pass


# prose files whose lines each state one fact about named lands, nets and parts: measured on the guide of 2026-11-13, the check (token or
# shared word) had no false alarm on the citations of these three; every other prose file had some (tables of numbers, notes), so it is not read
PROSE_FILES = {"design/ecad/band/band-interface.md", "design/mfg/assembly/process.md", "design/mfg/assembly/hotbar-joint.md"}
STOP_WORDS = set("which where there their these those about after before under above while without within between should would could shall other every each only also more than that this with from have been into onto over some when what then them they will must not are the and for".split())


def content_words(t):
    return {w[:6] for w in re.findall(r"[a-z][a-z0-9]{4,}", t.lower()) if w not in STOP_WORDS}


def word_in(tok, text):
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])", text) is not None


def tokens_in(seg):
    """Designators, part names (`outer_body`), nets and part models in a stretch of the guide."""
    out = []
    for name, rx in TOKEN_FORMS:
        for m in re.finditer(rx, seg):
            tok = m.group(1)
            if tok in NOT_TOKENS or (name == "designator" and (re.match(r"(?:S\d+|F\d+|K\d+|W\d\d+|G\d+|H\d+|N\d+)$", tok) or NOT_DESIGNATOR_BEFORE.search(seg[:m.start(1)]))):
                continue
            out.append(tok)
    out += [m.group(1) for m in re.finditer(r"`([a-z][a-z0-9]*_[a-z0-9_]+)`", seg)]
    for n in NET_NAMES:
        if word_in(n, seg):
            out.append(n)
    return sorted(set(out))


bad_t, n_t, n_checked = [], 0, 0
for i, l in enumerate(doc_lines, 1):
    ms = list(CITE.finditer(l))
    if not ms:
        continue
    is_row = l.startswith("|")
    prev_end = 0
    win_start = 0
    for k, m in enumerate(ms):
        n_t += 1
        item_nets, item_text = [], ""
        # a table row names its part in its own cells: every cell up to this citation is read (finding and item ids such as F6, K15, W12 are no designators); a sentence is read from the previous
        # citation (or the sentence start) to this citation; citations joined only by "; ", ", ", " to " or " and " form one group and share
        # the text before the group; the text up to 60 characters after the citation is read too for a label that follows it ("386 for DISP1"),
        # and the end line of a range ("98" in "87 to 98") is read against the group's tokens and the rest of the sentence
        gap = l[prev_end:m.start()]
        if k == 0 or re.search(r"[A-Za-z0-9]", re.sub(r"\b(?:to|and)\b", "", gap)):
            win_start = prev_end
        is_range_end = k > 0 and re.fullmatch(r"\W*to\W*", gap) is not None
        if is_row:
            toks = tokens_in(re.sub(r"`[^`]*:\d+`", " ", l[:m.start()]))   # the cells of the row up to this citation, without the citations
        else:
            win = l[win_start:m.start()]
            cut = win.rfind(". ")
            win = win[cut + 2:] if cut >= 0 else win
            in_range = is_range_end or (k + 1 < len(ms) and re.fullmatch(r"\W*to\W*", l[m.end():ms[k + 1].start()]) is not None)
            # a range "a to b" names a run of rows: its group's whole text is read; a single citation reads its item of the list
            # (a long list names many parts, and only the last item belongs to the citation)
            if not in_range:                                   # the item of a list: the text after the last "), " (or the previous citation)
                b = win.rfind("), ")
                win = win[b + 3:] if b >= 0 else win
            toks = tokens_in(win)
            if not toks:                                       # the sentence names none: the 250 characters before it are the context
                toks = tokens_in(l[max(0, m.start() - 250):m.start()])
            item_nets = [] if in_range else tokens_in(win)    # tokens named in the item itself (rule for prose files below)
            item_text = re.sub(r"`[^`]*:\d+`", " ", win)
            tail = l[m.end():ms[k + 1].start() if k + 1 < len(ms) else len(l)]
            if is_range_end:                                   # the end of a range "a to b": the group's text before it, and the sentence after it
                rest = l[m.end():]
                toks = sorted(set(toks) | set(tokens_in(rest[:rest.find(". ")] if ". " in rest else rest)))
            else:                                              # a label that follows the citation ("386 for DISP1")
                toks = sorted(set(toks) | set(tokens_in(tail[:tail.find(". ") if ". " in tail else 60][:60])))
        prev_end = m.end()
        path, ln = m.group(1), int(m.group(2))
        fp = os.path.join(REPO, path)
        # only a table line (a .csv row: bom.csv, placement.csv, netlist.csv, the position files, product-wiring.csv) is one part's row; a line of
        # prose may state a fact about the part without naming it, so prose citations are not read by this rule; line 1 of a table is its header
        # a prose file (.md, .txt, .py): a line may state a fact about a part without naming it, so designators and part names are not read;
        # a NET named in the citation's own item (no context, no range) must be named on the cited line (the 2.3 s of "tied to GND" is no row)
        prose = not path.endswith(".csv")
        if prose and path not in PROSE_FILES:
            continue
        if prose:
            toks = item_nets
        if not toks or int(ln) == 1 or not os.path.isfile(fp):
            continue
        flines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
        if ln < 1 or ln > len(flines):
            continue
        n_checked += 1
        # a designator or a part name must be in the row's key cells (the columns named ref, reference, part, item or net: the row's own
        # name), not merely somewhere in its text (a description may mention another part); a net or a part model may be anywhere on the line
        hdr = next(csv.reader([flines[0]]), [])
        row = next(csv.reader([flines[ln - 1]]), [])
        keys = " , ".join(c for h, c in zip(hdr, row) if re.fullmatch(r"(?i)ref|reference|part|item|net|name|\w+_ref", h.strip()))
        key_words = set(re.split(r"[\s,;]+", keys))
        def hit(t):
            if re.fullmatch(r"[A-Z]{1,4}\d{1,3}", t) or re.fullmatch(r"[a-z][a-z0-9]*_[a-z0-9_]+", t):
                return t in key_words
            return word_in(t, flines[ln - 1])
        if prose:   # a prose line is right when it holds one of the tokens or shares a content word with the item
            if any(word_in(t, flines[ln - 1]) for t in toks) or (content_words(item_text) & content_words(flines[ln - 1])):
                continue
        elif any(hit(t) for t in toks):
            continue
        if True:
            bad_t.append(f"line {i}: {path}:{ln} holds none of {', '.join(toks[:6])} (it holds: {flines[ln - 1].strip()[:60]})")
for b in bad_t:
    print("TOKEN " + b)
[print("T1BAD", x) for x in bad_t]
line("T1", not bad_t, f"all {n_checked} citations that name a designator, net or part find one on the cited line ({n_t} citations in all)" if not bad_t else f"{len(bad_t)} of {n_checked} citations do not hold what their sentence names (first: {bad_t[0][:150]})")

# (m) P1 and (n) L1: the guide against joints.csv and product-wiring.csv
def read_rows(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except OSError as e:
        return None


def step_text(n):
    return dict(steps).get(n, "")


jrows, wrows = read_rows(JOINTS), read_rows(WIRING)
line("X0", jrows is not None and wrows is not None and len(jrows) > 0 and len(wrows) > 0, "joints.csv and product-wiring.csv read" if jrows and wrows else f"cannot read {JOINTS} or {WIRING}")
jrows, wrows = jrows or [], wrows or []

# P1: the ribbon lands and their paste
bad_p = []
band = [r for r in jrows if re.search(r"ring main board J_BAND_[AB] land \d+", r["what_meets_what"])]
groups = {}
for r in band:
    mm = re.search(r"J_BAND_([AB]) land (\d+)", r["what_meets_what"])
    groups.setdefault("J_BAND_" + mm.group(1), set()).add(mm.group(2))
n_lands = sum(len(v) for v in groups.values())
pasted = [r for r in band if re.search(r"paste printed through .* in pass (\d) of step (\d+)", r["solder_source"])]
if not band:
    bad_p.append("joints.csv has no row for a J_BAND land")
if band and len(pasted) != len(band):
    bad_p.append(f"{len(band) - len(pasted)} of {len(band)} J_BAND rows of joints.csv name no paste printed in a pass of a step")
if pasted:
    pm = re.search(r"paste printed through .* in pass (\d) of step (\d+)", pasted[0]["solder_source"])
    ppass, pstep = pm.group(1), int(pm.group(2))
    jstep = int(pasted[0]["step"]) if pasted[0]["step"].strip().isdigit() else None
    t2 = step_text(pstep)
    sent = [x for x in re.split(r"(?<=[.!?])\s+|\n", t2) if "J_BAND" in x and "paste" in x.lower() and "land" in x]
    if not sent:
        bad_p.append(f"step {pstep} has no sentence that says the J_BAND lands get paste (joints.csv: paste printed in pass {ppass} of step {pstep})")
    for x in sent[:1]:
        if re.search(r"\bno paste\b|\bwithout paste\b|get none|bare", x, re.I):
            bad_p.append(f"step {pstep} says the ribbon lands get no paste, joints.csv says they get paste: {x.strip()[:100]}")
        for g, ls in sorted(groups.items()):
            mg = re.search(re.escape(g) + r" \((\d+) lands?\)", x)
            if not mg or int(mg.group(1)) != len(ls):
                bad_p.append(f"step {pstep} gives {g} as {mg.group(1) if mg else 'no land count'}, joints.csv has {len(ls)} lands")
        if not re.search(r"PASS %s\b" % ppass, x):
            bad_p.append(f"step {pstep} does not say PASS {ppass} for the ribbon lands")
    if jstep is not None:
        j14 = step_text(jstep)
        jj = re.search(r"^- \*\*Join:\*\* (.*)$", j14, flags=re.M)
        jt = jj.group(1) if jj else ""
        mm2 = re.search(r"on the solder layer that step (\d+) put on the (\d+) lands", jt)
        if re.search(r"bare lands", jt) or not mm2:
            bad_p.append(f"step {jstep} Join does not say 'on the solder layer that step {pstep} put on the {n_lands} lands'")
        elif int(mm2.group(1)) != pstep or int(mm2.group(2)) != n_lands:
            bad_p.append(f"step {jstep} says step {mm2.group(1)} put solder on {mm2.group(2)} lands, joints.csv says step {pstep} and {n_lands} lands")
        for g, ls in sorted(groups.items()):
            mg = re.search(re.escape(g) + r" \((\d+) lands?\)", jt)
            if not mg or int(mg.group(1)) != len(ls):
                bad_p.append(f"step {jstep} Join gives {g} as {mg.group(1) if mg else 'no land count'}, joints.csv has {len(ls)} lands")
line("P1", not bad_p, f"ribbon land paste: guide steps agree with joints.csv ({n_lands} lands, {', '.join('%s %d' % (g, len(v)) for g, v in sorted(groups.items()))})" if not bad_p else "; ".join(bad_p))

# L1: tabs, motor leads, charging discs
bad_l = []
tabs = {}
for r in wrows:
    if r["carrier_kind"] == "tab":
        mt = re.search(r"tab (P\+|P-|NTC)", r["carrier"])
        if mt:
            tabs[mt.group(1)] = (r["end_B_pin"].split(" ")[0], r["signal_B"])
for r in jrows:  # joints.csv orientation text against the wiring list
    mt = re.match(r"tab (P\+|P-|NTC) on land (\d+) \((\w+)\)", r["orientation"].strip())
    if mt and mt.group(1) in tabs and tabs[mt.group(1)] != (mt.group(2), mt.group(3)):
        bad_l.append(f"joints.csv {r['joint_id']} says tab {mt.group(1)} on land {mt.group(2)} ({mt.group(3)}), product-wiring.csv has land {tabs[mt.group(1)][0]} ({tabs[mt.group(1)][1]})")
tabrow = next((r for r in jrows if r["wiring_line"] in {w["id"] for w in wrows if w["carrier_kind"] == "tab"} and r["step"].strip().isdigit()), None)
if len(tabs) != 3 or tabrow is None:
    bad_l.append(f"product-wiring.csv has {len(tabs)} tab lines (3 wanted) or joints.csv has no row for them")
else:
    ts = step_text(int(tabrow["step"]))
    found = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r"[Tt]ab (P\+|P-|NTC) (?:goes )?on land (\d+) \((\w+)\)", ts)}
    for t, (land, net) in sorted(tabs.items()):
        if t not in found:
            bad_l.append(f"step {tabrow['step']} does not say 'tab {t} on land {land} ({net})' (a form the check reads)")
        elif found[t] != (land, net):
            bad_l.append(f"step {tabrow['step']} puts tab {t} on land {found[t][0]} ({found[t][1]}), product-wiring.csv has land {land} ({net})")
    mo = re.search(r"in the order ((?:P\+|P-|NTC)(?:, (?:P\+|P-|NTC)){2}) from the slot[^.]*?lands (\d), (\d), (\d)", ts)
    if not mo:
        bad_l.append(f"step {tabrow['step']} does not give the tab order and the lands in the form 'in the order P+, NTC, P- from the slot ... lands 1, 3, 2'")
    else:
        want = [tabs[t][0] for t in mo.group(1).split(", ") if t in tabs]
        if want != [mo.group(2), mo.group(3), mo.group(4)]:
            bad_l.append(f"step {tabrow['step']} says the tabs in the order {mo.group(1)} lie on lands {mo.group(2)}, {mo.group(3)}, {mo.group(4)}; product-wiring.csv gives lands {', '.join(want)}")
# motor leads: guide step of the M1 lead rows
mleads = {}
tailof = {}
for r in wrows:
    if r["carrier_kind"] == "copper" and r["end_B_ref"] == "M1":
        tailof[r["end_B_pin"].split(" ")[0]] = r["end_A_pin"].split(" ")[0]
for r in wrows:
    if r["carrier_kind"] == "lead" and r["end_A_ref"] == "M1":
        land = r["end_B_pin"].split(" ")[0]
        mleads[land] = (r["signal_B"], tailof.get(land), r["carrier_marking"].split(" ")[0])
mrow = next((r for r in jrows if r["wiring_line"] in {w["id"] for w in wrows if w["carrier_kind"] == "lead" and w["end_A_ref"] == "M1"} and r["step"].strip().isdigit()), None)
if not mleads or mrow is None:
    bad_l.append("product-wiring.csv has no motor lead line or joints.csv no row for it")
else:
    ms_ = step_text(int(mrow["step"]))
    for land, (net, tail, colour) in sorted(mleads.items()):
        if not re.search(r"land %s(?: of the motor lands)?, net %s, joined to land %s\b" % (land, re.escape(net), tail), ms_):
            bad_l.append(f"step {mrow['step']} does not say 'land {land}, net {net}, joined to land {tail}' (product-wiring.csv)")
        if not re.search(r"on land %s \(%s\)" % (tail, re.escape(net)), ms_):
            bad_l.append(f"step {mrow['step']} check does not name tail land {tail} as ({net}) (product-wiring.csv)")
    mr = re.search(r"the (\w+) lead to the \+ land", ms_)
    plus = [v for k, v in mleads.items() if v[0] == "VMOT"]
    if plus and (not mr or mr.group(1) != plus[0][2]):
        bad_l.append(f"step {mrow['step']} puts the {mr.group(1) if mr else 'no colour'} lead on the + land, product-wiring.csv says {plus[0][2]}")
# charging discs: "VBUS to land 4, D- to land 5, ..." against the copper lines J_BAND_B land -> CPk
discs = {}
for r in wrows:
    if r["carrier_kind"] == "copper" and re.match(r"CP\d$", r["end_B_ref"]):
        discs[r["signal_A"]] = r["end_A_pin"].split(" ")[0]
drow = next((r for r in jrows if re.match(r"disc", r["what_meets_what"]) is None and "CP1" in r["what_meets_what"] and r["step"].strip().isdigit()), None)
if not discs:
    bad_l.append("product-wiring.csv has no copper line to CP1 to CP4")
else:
    dst = step_text(int(drow["step"])) if drow else step_text(8)
    md = re.search(r"VBUS to land (\d), D- to land (\d), D\+ to land (\d), GND to land (\d)", dst)
    if not md:
        bad_l.append("the disc step does not give 'VBUS to land N, D- to land N, D+ to land N, GND to land N'")
    else:
        for net, got in zip(("VBUS", "USB_DN", "USB_DP", "GND"), md.groups()):
            if discs.get(net) != got:
                bad_l.append(f"the disc step puts {net} on land {got}, product-wiring.csv has land {discs.get(net)}")
line("L1", not bad_l, "guide steps 7, 8 and 9 agree with product-wiring.csv and joints.csv on tab lands, motor lands and disc lands" if not bad_l else "; ".join(bad_l))

# (g) last line
last = doc_lines[-1] if doc_lines else ""
line("G1", last.startswith("RESULT:"), f"last line starts with RESULT: ({last[:60]})")

print(f"RESULT PASS" if not fails else f"RESULT FAIL {', '.join(fails)}")
sys.exit(0 if not fails else 1)
