
## 2. check_joints.py (fault I2)

Rules added (data tables at `check_joints.py` lines 45 to 62, functions `weak_check` line 87 and `weak_heat` line 106; header documents them):

| rule | a row fails when | accepted forms (the data) |
|---|---|---|
| R6 weak-check | its check field has no METHOD form or no PASS form | METHOD: an instrument (ohmmeter, meter, continuity, probe, needle tips, diode mode, feeler, gauge, thermocouple, bench supply, jig, X-ray), a way of looking (inspection, optical, magnifier, microscope, by eye, "N times"), a named test or reading (T-xxx, FACTORY ENTER, GET_INFO, USB through, beep, reads, voltage, measured, height, lights). PASS: a number with a unit (mm V A mA ohm kohm k Mohm C C/s N s ms MB MHz %, a magnification "20 times" is not one), a named reading (beeps, no beep, reads open, reads the cell voltage, a diode drop, enumerates, answers, vibrates, 0 violations, continuity, positive, breathing, blink), a named visual condition (flat, no bridge, not tilted, no tilt, not skewed, touch nothing else, none of its tails lifted, in place, centred), "accept rules of step N" where step N of assembly.md exists and names its accept rules, or `file:N` whose line N exists and itself holds a pass form |
| R7 weak-heat | its heat field is not a HEAT form | a value with a unit (C, degrees C, s, seconds, N) together with a tool or process word (iron, tip, hot bar, blade, thermode, hot plate, reflow, oven, profile, pressed contact, hand solder) in the heat text or in the row's own tool field; or a profile Pn with `process.md Pn` and the section `## Pn.` existing in process.md; or `none` or `no heat` followed by `:` and a reason of 6 or more characters |

Dry run on the real table first, without failing (`--list-weak`, exit 0): table of 17:40 (`copies/joints-snapshot-1.csv`): 1 row would be rejected, `final/check_joints-list-weak-snapshot1-final-rules.log`:
`WEAK R6 J-W027-A | names no pass value or pass condition | land B3, FACTORY ENTER and T-CHARGE pass at the end of the step; an open NTC land reads as cold and T-CHARGE fails with the charger off (hotbar-joint.md section 4)`. The same dry run with the first version of my rules (`joints/dry-run-list-weak.log`, `joints/dry-run-list-weak-2.log`) gave the same 1 row. For the owner of `joints.csv` (guide-fix4): R6 rejected J-W027-A (a named firmware test without its pass value or a citation of it). It has since amended that check ("as step 14 Check (c) says (design/mfg/assembly/assembly.md:205)"): table of 17:45 (`copies/joints-snapshot-2.csv`) and the live table at the end: `WEAK 0 lines in 99 rows` (`final/check_joints-list-weak-snapshot2.log`, `final/check_joints-list-weak-live.log`); `final/joints-W027-before-after.log` shows the two texts. R7 rejected no real row (no R7 line in the dry runs above).

Bar for the existing tests: the mini table of `tests/run_tests.py` has a check "fake continuity [needs case 8]" and a heat "fake 300 C 2 s" with tool "fake iron". Two accommodations so that those tests pass unchanged: "continuity" counts as a named reading (a continuity test passes or fails), and the tool word of a heat may come from the row's tool field; an EMPTY tool field is left to R2 (otherwise the existing `field_emptied` copies would show an R7 line besides R2). See the questions at the end.

Reviewer's faults: result before and after.

| reviewer's copy | before (`fakes-check_joints.log`) | after |
|---|---|---|
| J-W026-A check = "ok" | passed (`RESULT PASS`) | exit 1, `R6 weak-check: J-W026-A check names no method (what is measured or looked at): 'ok'` (`logs/cj/rev_check_ok.log`, and the reviewer's file `rev_checkok_file`) |
| J-W061-B heat = "hot" | passed | exit 1, `R7 weak-heat: J-W061-B heat names no value with a unit (C, s, N) ...: 'hot'` (`logs/cj/rev_heat_hot.log`, `rev_heatok_file`) |
| the other fakes (8 re-run as files) | failed | the reviewer's files `rev_checkempty rev_dropped rev_empty rev_flood rev_gap rev_stepbad rev_brokenpaste rev_nofile` still exit 1 |
