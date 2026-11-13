import re, sys
F = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware")
notes = open(F + "/docs/power-notes.md").read()
L = open(F + "/build-logs/step6/u5-run2.console").read().split("\n")
# every "L NNN" / numbers after "L line(s)" and the lists in section 2 and 3 tables: collect numbers 20..1700 that follow 'L ' or sit in the line lists
nums = set()
for m in re.finditer(r"\bL (?:lines? )?([0-9][0-9, and to]*)", notes):
    for n in re.findall(r"\d+", m.group(1)):
        nums.add(int(n))
for m in re.finditer(r"(?:copy|copies)[^\n]*?((?:L )?\d{3,4}(?:, \d{3,4})+)", notes):
    for n in re.findall(r"\d+", m.group(1)):
        nums.add(int(n))
for sec in re.findall(r"(?m)^(?:All 10 copies|The 5 build copies).*?(?=\n\n)", notes, re.S):
    for n in re.findall(r"\b(\d{3,4})\b", sec):
        nums.add(int(n))
bad = 0
for n in sorted(nums):
    if 1 <= n <= len(L):
        print(n, L[n - 1][:110])
    else:
        print("NO LINE", n); bad += 1
print("claims checked:", len(nums), "no match:", bad)
