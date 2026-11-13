import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
T1726 = 'section(arch, r"^### 17\\.26 ", r"^### |^## ") or ""'
R1726 = 'r"^\\| US (\\d+) \\| [^|]+\\| [^|]+\\| [\\d.]+ mm \\| ([\\d.]+) to ([\\d.]+) mAh \\|"'
reps = [
('      the motor charge rule; section 7 protocol sentence; per-size tables.\n"""',
 '      the motor charge rule; section 7 protocol sentence; per-size tables.\n'
 '  Changed and added for F6 (architecture 17.26, measured cells):\n'
 '  7, 16. (changed) the cells per size are read from the 17.26 table (F5: 17.17);\n'
 '      the 8.1 compile limit equals 1 C of the smallest cell (17,600 uA);\n'
 '      the current-microamp row names 17.6 mAh and 0.85 C (F5: 18.2 and 0.82).\n'
 '  13, 16. (changed) the change lists run from "Changes from F5 to F6"; header\n'
 '      Version F6 with sections 17.11 to 17.26; the F5 to F6 list has 4 items.\n'
 '  19. F6 rule: outside the change lists no line names 18.2, 24.3 or 32.9 (mAh\n'
 '      of the calculated cells of 17.17) or 18,200 (their compile limit) unless\n'
 '      the line holds the word "before".\n"""'),
('    a = fw.find("Changes from F4 to F5")', '    a = fw.find("Changes from F5 to F6")'),
('        errors.append("change list \'Changes from F4 to F5\' before \'How to read this:\' not found")',
 '        errors.append("change list \'Changes from F5 to F6\' before \'How to read this:\' not found")'),
('        a1717 = section(arch, r"^### 17\\.17 ", r"^### |^## ") or ""\n        caps = [(float(a), float(b)) for a, b in re.findall(r"^\\| US \\d+ \\| [\\d.]+ mm \\| ([\\d.]+) to ([\\d.]+) mAh \\|", a1717, re.M)]',
 '        a1726 = ' + T1726 + '\n        caps = [(float(a), float(b)) for u, a, b in re.findall(' + R1726 + ', a1726, re.M)]'),
('is above 1 C of the smallest cell {cmin} mAh (architecture 17.17)")',
 'is above 1 C of the smallest cell {cmin} mAh (architecture 17.26)")\n'
 '        lim = re.search(r"A build fails to compile when it is unset, above ([\\d,]+) \\(1 C of the smallest cell, ([\\d.]+) mAh", s81)\n'
 '        if not lim or cmin is None or int(lim.group(1).replace(",", "")) != round(cmin * 1000) or float(lim.group(2)) != cmin:\n'
 '            errors.append(f"8.1 compile limit {lim and lim.groups()} is not 1 C of the smallest cell {cmin} mAh of architecture 17.26")'),
('    if not re.match(r"^# .*\\n\\nVersion F5, ", fw):\n        errors.append("header does not say Version F5")',
 '    if not re.match(r"^# .*\\n\\nVersion F6, ", fw):\n        errors.append("header does not say Version F6")'),
('follows[^\\n]{0,80}sections 17\\.11 to 17\\.23", head, re.I):\n        errors.append("header does not say it follows architecture sections 17.11 to 17.23")',
 'follows[^\\n]{0,80}sections 17\\.11 to 17\\.26", head, re.I):\n        errors.append("header does not say it follows architecture sections 17.11 to 17.26")'),
('    for lst in ("Changes from F4 to F5", "Changes from F3 to F4", "Changes from F2 to F3"):',
 '    for lst in ("Changes from F5 to F6", "Changes from F4 to F5", "Changes from F3 to F4", "Changes from F2 to F3"):'),
('        errors.append(f"\'Changes from F4 to F5\' must hold 8 numbered items, one per point of the brief: {items}")',
 '        errors.append(f"\'Changes from F4 to F5\' must hold 8 numbered items, one per point of the brief: {items}")\n'
 '    f6list = section(fw, r"^Changes from F5 to F6", r"^(?!\\d+\\. )\\S") or ""\n'
 '    if re.findall(r"^(\\d+)\\. \\*\\*", f6list, re.M) != ["1", "2", "3", "4"]:\n'
 '        errors.append("\'Changes from F5 to F6\' must hold 4 numbered items")'),
('    a1717 = section(arch, r"^### 17\\.17 ", r"^### |^## ") or ""\n    size_rows = re.findall(r"^\\| US (\\d+) \\| [\\d.]+ mm \\| ([\\d.]+) to ([\\d.]+) mAh \\|", a1717, re.M)',
 '    a1726b = ' + T1726 + '\n    size_rows = re.findall(' + R1726 + ', a1726b, re.M)'),
('    pm = re.search(r"Time left at ([\\d.]+) mA on ([\\d.]+) mAh \\[CALC\\]: B15',
 '    pm = re.search(r"Time left at ([\\d.]+) mA on ([\\d.]+) mAh \\[CALC[^\\]]*\\]: B15'),
('(architecture 17.17 table, firmware 8.5', '(architecture 17.26 table, firmware 8.5'),
('differs from architecture 17.17 {cmin} to {cmax}")', 'differs from architecture 17.26 {cmin} to {cmax}")'),
('    for need in ("CHARGE_CURRENT", "15,000", "18.2 mAh", "0.82 C", "S12"):',
 '    for need in ("CHARGE_CURRENT", "15,000", "17.6 mAh", "0.85 C", "S12"):'),
('    # 5. end matter',
 '    # 19. F6: no value of the calculated cells of 17.17 as a current value\n'
 '    stale = re.compile(r"(?<![\\d.,])(18\\.2|24\\.3|32\\.9)(?![\\d])|18,200|(?<!\\d)18200(?!\\d)")\n'
 '    nstale = 0\n'
 '    for i, ln in enumerate(body.splitlines(), 1):\n'
 '        m = stale.search(ln)\n'
 '        if m and "before" not in ln.lower():\n'
 '            nstale += 1\n'
 '            errors.append(f"former cell value \'{m.group(0)}\' named as a current value (body line {i}, outside the change lists): {ln[:70]}")\n'
 '    print(f"check 19 former cell values: {nstale} lines name 18.2, 24.3, 32.9 or 18,200 without \'before\'")\n\n'
 '    # 5. end matter'),
]
bad = 0
for a, b in reps:
    n = s.count(a)
    print(n, a[:70].replace("\n", " "))
    if n == 1:
        s = s.replace(a, b)
    else:
        bad += 1
open(p, "w", encoding="utf-8").write(s)
print("not applied:", bad)
