# Fakes for design/mfg/assembly/check_assembly.py through its path argument (copies of assembly.md in W).
import os, re, subprocess
W = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work")
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
PY = ROOT + "/design/.venv/bin/python"
CHK = ROOT + "/design/mfg/assembly/check_assembly.py"
DOC = ROOT + "/design/mfg/assembly/assembly.md"
FK = W + "/fakes-ca"; os.makedirs(FK, exist_ok=True)
txt = open(DOC).read()
def write(name, t):
    p = os.path.join(FK, name + ".md"); open(p, "w").write(t); return p
cases = [("honest_copy", write("honest", txt), 0)]
# 1 a step without its Check field
t = txt.replace("- **Check:** both joints pass the accept rules of step 2. Apply 3.0 V", "- both joints pass the accept rules of step 2. Apply 3.0 V", 1)
cases.append(("step7_no_check_field", write("nocheck", t), 1))
# 2 last line removed
cases.append(("no_result_line", write("noresult", txt.rsplit("\nRESULT:", 1)[0] + "\n"), 1))
# 3 G1 reintroduced: the ribbon lands get no paste and step 14 has no solder
t = re.sub(r"- \*\*The 15 ribbon lands:\*\*[^\n]*\n", "- **The 15 ribbon lands:** J_BAND_A and J_BAND_B get no paste.\n", txt, count=1)
t = t.replace("by hot bar, on the solder layer that step 2 put on the 15 lands", "by hot bar, on the bare lands", 1)
cases.append(("G1_reintroduced", write("g1", t), 1))
# 4 a wrong land in the cell tab sentence (P+ on land 2)
t = txt.replace("Tab P+ goes on land 1 (VBAT), tab NTC on land 3 (NTC), tab P- on land 2 (GND).", "Tab P+ goes on land 2 (GND), tab NTC on land 3 (NTC), tab P- on land 1 (VBAT).", 1)
cases.append(("cell_tabs_swapped", write("tabs", t), 1))
# 5 a citation to a line that holds other text (existing line number)
t = txt.replace("(`design/ecad/band/band-interface.md:123`). The red lead is the + lead", "(`design/ecad/band/band-interface.md:3`). The red lead is the + lead", 1)
cases.append(("citation_wrong_line", write("cite", t), 1))
# 6 a citation past the end of the file
t = txt.replace("(`design/ecad/band/band-interface.md:123`). The red lead is the + lead", "(`design/ecad/band/band-interface.md:9999`). The red lead is the + lead", 1)
cases.append(("citation_past_end", write("cite2", t), 1))
# 7 flood: the whole section 2 twice (repeated step numbers)
i = txt.index("### Step 1."); j = txt.index("## 3. Order conflicts")
cases.append(("flood_steps_twice", write("flood", txt[:j] + txt[i:j] + txt[j:]), 1))
# 8 empty file
cases.append(("empty", write("empty", ""), 1))
differs = 0
for name, p, want in cases:
    r = subprocess.run([PY, "-I", CHK, p], capture_output=True, text=True)
    open(os.path.join(FK, name + ".log"), "w").write(r.stdout + r.stderr)
    lines = (r.stdout + r.stderr).strip().splitlines(); last = lines[-1] if lines else ""
    got = 0 if r.returncode == 0 else 1; ok = got == want; differs += 0 if ok else 1
    print("CASE %-22s want_exit=%d got_exit=%d %s | %s" % (name, want, r.returncode, "as expected" if ok else "DIFFERS", last[:160]))
print("RESULT fakes=%d differs=%d" % (len(cases), differs))
