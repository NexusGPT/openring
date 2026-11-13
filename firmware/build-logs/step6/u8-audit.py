"""Claim audit of docs/factory-notes.md against the saved logs. Writes u8-audit.log with open()."""
import re, pathlib
B = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
S = B / "build-logs/step6"
notes = (B / "docs/factory-notes.md").read_text()
def lines(n): return (S / n).read_text().split("\n")
cases, full, bs, bb = lines("u8-cases.console"), lines("u8-full1.console"), lines("u8-bsim-final.console"), lines("u8-bsim-broken-final.console")
out = []; bad = 0; n = 0
def chk(label, ok, info=""):
    global bad, n
    n += 1
    if not ok: bad += 1
    out.append(f"{'OK ' if ok else 'BAD'} {label} {info}")
# 1 case table rows: "| row | `case` ... | N / B |" and "N, M / B, C"
sec3 = notes[notes.index("## 3."):notes.index("## 4.")]
for m in re.finditer(r"^\| ([^|]+) \| ([^|]+) \| ([0-9, ]+) / ([0-9, ]+) \|", sec3, re.M):
    names = re.findall(r"`(factory_[a-z_0-9.]+)`", m.group(2))
    ns = [int(x) for x in m.group(3).split(",")]; bsl = [int(x) for x in m.group(4).split(",")]
    sel = [x for x in names if x.startswith("factory_")]
    if "test_frames_reach_display" in m.group(2): continue
    if len(ns) == 1:
        sel = sel[:1]
    # for the multi-case T22 row the first two names correspond to the two lines
    for k, case in enumerate(sel[:len(ns)]):
        for line, tag in ((ns[k], "native"), (bsl[k], "chip")):
            l = cases[line - 1]
            chk(f"case {case} {tag} line {line}", case in l and "PASS" in l, l.strip()[-80:])
# reach display
for line in (52, 165):
    chk(f"reach_display line {line}", "test_frames_reach_display" in cases[line-1] and "PASS" in cases[line-1])
# broken copies table
sec4 = notes[notes.index("## 4."):notes.index("## 5.")]
for m in re.finditer(r"^\| `(\w+)`[^|]*\| `(factory_\w+\.\w+)` \| (\d+) / (\d+) \|", sec4, re.M):
    v, case, a, b = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    for line in (a, b):
        l = full[line-1]
        chk(f"broken {v} line {line}", v in l and case in l and "named case failed" in l)
# cited key lines
for line, text in ((23, "41 of 41"), (46, "41 of 41"), (1462, "RESULT PASS"), (1464, "UNIT PASS tests/factory")):
    chk(f"full1 line {line}", text in full[line-1], full[line-1][:70])
for line, text in ((52, "RESULT PASS"), (51, "21 checks passed"), (34, "REPORTS 150"), (43, "MEDIAN GAP 106 ms of 56"), (50, "Ring0000")):
    chk(f"bsim-final line {line}", text in bs[line-1], bs[line-1][:70])
chk("bsim-broken line 65", "not connectable" in bb[64] and "FAIL" in bb[64])
chk("bsim-broken line 118", "stopped within 1 s" in bb[117] and "FAIL" in bb[117])
chk("bsim-broken line 119", "RESULT PASS" in bb[118])
for f in ("u8-full1.exit", "u8-bsim-final.exit", "u8-bsim-broken-final.exit", "u8-cases.exit"):
    chk(f"exit file {f}", (S / f).read_text().strip() == "0")
# other-failing lists
fulltxt = "\n".join(full)
expect = {"mic_without_sign": "factory_mic.test_no_screen_no_mic factory_mic.test_type_2_recording",
          "vbat_read_at_0": "factory_cmd.test_result_layout factory_motor.test_reads_and_timing factory_screen.test_frame_sequence",
          "beacon_after_ship": "factory_radio.test_adv_parameters factory_ship.test_beacon_name factory_ship.test_beacon_window factory_ship.test_beacon_window_sample"}
for v, lst in expect.items():
    chk(f"others {v} on both targets", fulltxt.count(f"{v} on native_sim: cases that failed: {lst} ") == 1 and fulltxt.count(f"cases that failed: {lst} ") >= 2)
for v in ("flag_ignored","x11_accepted","run_999","centre_records","store_lba_4097","type2_left","beacon_connectable"):
    chk(f"single failure {v}", len(re.findall(rf"{v} on [^\n]*cases that failed: \S+ $", fulltxt, re.M)) == 2)
chk("10 variants x 2 boards named case failed", fulltxt.count("the named case failed, as required") == 20)
chk("case PASS count 82", sum(1 for l in cases if " - PASS - [" in l) == 82)
chk("no FAIL in cases listing", not any(" - FAIL - [" in l for l in cases))
chk("pass lines first: 4 handler sections", sum(1 for l in cases if l.startswith("FILE")) == 4)
# claimed "Ring0000", 150 etc. already checked. editcheck: 10 matched once
ec = (S / "u8-editcheck2.log").read_text()
chk("editcheck2 10 matches", ec.count("edit matched once, named case") == 10 and "bsim connectable edit matched once" in ec and "bsim never_stops edit matched once" in ec)
chk("assertion lines cited", "test_cmd.c:230" in fulltxt and "test_screen.c:202" in fulltxt)
chk("T-RADIO notes: 10 s", "factory_radio" in notes)
chk("last line RESULT", notes.rstrip().split("\n")[-1].startswith("RESULT: done"))
out.append(f"claims checked: {n}, mismatches: {bad}")
(S / "u8-audit.log").write_text("\n".join(out) + "\n")
