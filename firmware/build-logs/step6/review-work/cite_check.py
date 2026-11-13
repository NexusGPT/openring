"""B4 check: for each sampled citation of a unit's notes, open the cited log and print the cited line (or the first
matching line when the note gives no line) and whether every expected text is on it. Usage: python3 -I cite_check.py
Output: one line per citation, then per-unit counts and a total."""
import pathlib

L = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware/build-logs/step6"))
B = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware/build-logs"))
T = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware/tests"))
# (unit, notes claim (short), file, line or None or "last", [texts that must be on that line])
C = [
    ("rhw", "rhw-notes l.409 final last result line 606", L / "u0-20261113-044107-u-rhw.log", 606, ["UNIT PASS tests/rhw"]),
    ("rhw", "rhw-notes l.409 last line local log", L / "u0-20261113-044107-u-rhw.log", "last", ["# local log:", "20261113-044107-u-rhw.log"]),
    ("rhw", "rhw-notes l.405 run 1 result", L / "u0-20261113-043354-u-rhw.log", None, ["UNIT FAIL tests/rhw tests-native_sim tests-nrf54lm20bsim_nrf54lm20a_cpuapp broken-rhw"]),
    ("rhw", "rhw-notes l.397 K14 line in run 2", L / "u0-20261113-043605-u-rhw.log", None, ["K14: sys_clock_hw_cycles_per_sec 1000000; k_cycle_get_32 advanced 100100"]),
    ("rhw", "rhw-notes l.415 223 defines, 196 found", L / "u0-check-spec-lines.log", None, ["223"]),
    ("rhw", "rhw-notes l.407 42 of 42 (native_sim)", L / "u0-20261113-044107-u-rhw.log", None, ["42 of 42"]),
    ("core", "core-notes step6 count rows COUNT MATCH", L / "u1-count-rows-1.log", "last", ["COUNT MATCH"]),
    ("core", "core-notes step6 host 221 pass", L / "u1-host-2.log", None, ["RESULT PASS tests=221"]),
    ("core", "core-notes step6 broken host 26", L / "u1-broken-host-1.log", None, ["BROKEN ALL PASS 26 copies"]),
    ("core", "core-notes step6 unit-run2 line 60", L / "u1-unit-run2.stdout", 60, ["UNIT PASS tests/core tests/screens tests/control tests/relay"]),
    ("core", "core-notes step6 core-run1 last UNIT PASS", L / "u1-core-run1.stdout", None, ["UNIT PASS tests/core"]),
    ("store", "store-notes cited run l.1563", L / "u2-final10.console", 1563, ["RESULT PASS"]),
    ("store", "store-notes cited run l.1565", L / "u2-final10.console", 1565, ["UNIT PASS tests/store"]),
    ("store", "store-notes cited run l.1567", L / "u2-final10.console", 1567, ["# remote exit code: 0"]),
    ("store", "S2 test_rail_sequence l.214", L / "u2-cases10.console", 214, ["test_rail_sequence", "PASS"]),
    ("store", "S2 test_rail_sequence l.524", L / "u2-cases10.console", 524, ["test_rail_sequence", "PASS"]),
    ("store", "C3 test_s30_sfull_edges l.163", L / "u2-cases10.console", 163, ["test_s30_sfull_edges", "PASS"]),
    ("store", "S7 test_chunk_header_bytes l.366", L / "u2-cases10.console", 366, ["test_chunk_header_bytes", "PASS"]),
    ("store", "broken sfull_17 named case l.814", L / "u2-final10.console", 814, ["test_s30_sfull_edges"]),
    ("audio", "audio-notes A15 ring_two l.1310", L / "u3-run1-final.log", 1310, ["ring"]),
    ("audio", "audio-notes A15 ring_two l.1320", L / "u3-run1-final.log", 1320, ["ring"]),
    ("audio", "audio-notes C13 highlight_release_time l.540", L / "u3-run2-final.log", 540, ["test_highlight_frame_from_down_time"]),
    ("audio", "audio-notes C13 highlight_release_time l.602", L / "u3-run2-final.log", 602, ["test_highlight_frame_from_down_time"]),
    ("audio", "audio-notes run 2 46 of 46", L / "u3-run2-final.log", None, ["46 of 46"]),
    ("audio", "audio-notes run 2 UNIT PASS", L / "u3-run2-final.log", None, ["UNIT PASS tests/audio"]),
    ("xfer", "xfer-notes 47 of 47", L / "u4-20261113-065605-unit2.log", None, ["47 of 47 executed test cases passed"]),
    ("xfer", "xfer-notes last line local log", L / "u4-20261113-065605-unit2.log", "last", ["# local log:", "20261113-065605-u4-unit2.log"]),
    ("xfer", "xfer-notes UNIT PASS", L / "u4-20261113-065605-unit2.log", None, ["UNIT PASS tests/xfer"]),
    ("xfer", "xfer-notes C21 static checks 0 hits", L / "u4-static-checks.log", None, ["RESULT C21", "0 hits"]),
    ("xfer", "xfer-notes K3c counts 0 usbh_xfer_alloc", L / "20261113-063327-u4-k3c.log", None, ["usbh_xfer_alloc"]),
    ("power", "power-notes L line 22", L / "u5-run2.console", 22, ["executed test cases passed"]),
    ("power", "power-notes L line 44", L / "u5-run2.console", 44, ["executed test cases passed"]),
    ("power", "power-notes P19 L 69 test_pof_untouched", L / "u5-run2.console", 69, ["test_pof_untouched"]),
    ("power", "power-notes P2 cc copies L 1450", L / "u5-run2.console", 1450, ["cc_"]),
    ("power", "power-notes UNIT PASS", L / "u5-run2.console", None, ["UNIT PASS tests/power"]),
    ("motor", "motor-notes line 520 RESULT PASS", L / "u6-unit-run1.log", 520, ["RESULT PASS"]),
    ("motor", "motor-notes line 522 last result", L / "u6-unit-run1.log", 522, ["UNIT PASS tests/motor"]),
    ("motor", "motor-notes short run 28 of 28", L / "u6-short-run1.log", None, ["28 of 28"]),
    ("motor", "motor-notes exit file 0", L / "u6-unit-run1.exit", 1, ["0"]),
    ("motor", "motor-notes editcheck", L / "u6-editcheck.log", None, ["motor_player.test_vibration_off_keeps_the_others"]),
    ("sys", "sys-notes line 1169 UNIT PASS", L / "u7-full1.log", 1169, ["UNIT PASS tests/sys"]),
    ("sys", "sys-notes line 1167 RESULT PASS", L / "u7-full1.log", 1167, ["RESULT PASS"]),
    ("sys", "sys-notes 24 of 24 native_sim (lines 8 to 29)", L / "u7-full1.log", None, ["24 of 24"]),
    ("sys", "sys-notes exit file", L / "u7-full1.exit", 1, ["0"]),
    ("sys", "sys-notes editcheck RESULT PASS", L / "u7-editcheck.log", None, ["RESULT PASS"]),
    ("factory", "factory-notes line 23", L / "u8-full1.console", 23, ["41 of 41 executed test cases passed"]),
    ("factory", "factory-notes line 46", L / "u8-full1.console", 46, ["41 of 41 executed test cases passed"]),
    ("factory", "factory-notes line 1462 RESULT PASS", L / "u8-full1.console", 1462, ["RESULT PASS"]),
    ("factory", "factory-notes line 1464 UNIT PASS", L / "u8-full1.console", 1464, ["UNIT PASS tests/factory"]),
    ("factory", "factory-notes bsim line 52", L / "u8-bsim-final.console", 52, ["RESULT PASS"]),
    ("factory", "factory-notes bsim broken line 119", L / "u8-bsim-broken-final.console", 119, ["RESULT PASS"]),
    ("recorder", "recorder-notes line 22 43 of 43", L / "j-unit1.log", 22, ["43 of 43"]),
    ("recorder", "recorder-notes line 44 43 of 43", L / "j-unit1.log", 44, ["43 of 43"]),
    ("recorder", "recorder-notes UNIT PASS tests/recorder", L / "j-unit1.log", None, ["UNIT PASS tests/recorder"]),
    ("recorder", "C1 j-cases1 l.19", L / "j-cases1.log", 19, ["recorder_rows.mic_rail_only_in_recording", "passed"]),
    ("recorder", "C4 j-cases1 l.29", L / "j-cases1.log", 29, ["recorder_actions.close_order", "passed"]),
    ("recorder", "broken mic_before_sign l.84", L / "j-unit1.log", 84, ["test_start_draws_sign_before_mic"]),
    ("recorder", "exit file j-unit1.exit", L / "j-work" / "j-unit1.exit", 1, ["0"]),
    ("recorder", "j-stages1 STAGES PASS", L / "j-stages1.log", None, ["STAGES PASS"]),
    ("screens", "screens-notes u9 line 650 RESULT PASS", L / "u9-unit-run2.log", 650, ["RESULT PASS"]),
    ("screens", "screens-notes u9 line 652 UNIT PASS", L / "u9-unit-run2.log", 652, ["UNIT PASS"]),
    ("screens", "screens-notes u9 line 22 56 of 56", L / "u9-unit-run2.log", 22, ["56 of 56"]),
    ("screens", "screens-notes u9 line 44 56 of 56", L / "u9-unit-run2.log", 44, ["56 of 56"]),
    ("screens", "screens-notes compare RESULT EQUAL", L / "j-work" / "j-compare-screens.txt", "last", ["RESULT EQUAL"]),
]
per = {}
for unit, claim, f, line, texts in C:
    ok = False
    shown = ""
    where = ""
    if not f.exists():
        shown = "FILE MISSING"
    else:
        lines = f.read_text(errors="replace").splitlines()
        if line == "last":
            idx = len(lines) - 1
            cand = [idx] if lines else []
        elif isinstance(line, int):
            cand = [line - 1] if 0 < line <= len(lines) else []
        else:
            cand = [i for i, s in enumerate(lines) if all(t in s for t in texts)][:1]
        if cand:
            i = cand[0]
            shown = lines[i].strip()[:200]
            where = f"l.{i + 1}"
            ok = all(t in lines[i] for t in texts)
        else:
            shown = "NO SUCH LINE OR NO MATCH"
    per.setdefault(unit, [0, 0])
    per[unit][1] += 1
    per[unit][0] += 1 if ok else 0
    print(f"{'MATCH' if ok else 'NO MATCH'} | {unit} | {claim} | {f.name} {where} | {shown}")
print("---")
tot_ok = sum(v[0] for v in per.values())
tot = sum(v[1] for v in per.values())
for u, (a, b) in per.items():
    print(f"unit {u}: {a} of {b} citations match")
print(f"TOTAL {tot_ok} of {tot} citations match")
