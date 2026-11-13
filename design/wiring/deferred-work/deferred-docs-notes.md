# Deferred document items: notes

Run 2026-11-13, 20:04 to 20:12 CET (clock from `date`). ROOT = .. W = ROOT/design/wiring/deferred-work/docs-pass/ (copies before: `*.before.*`, diffs `*.diff`, logs, scripts). No git write, no browser, no web request.

## Item 158: architecture.md (943 lines now, 941 before)
Of the lines the earlier pass named (23, 300, 356, 369, 433, 455, 482, 515), lines 300, 356, 369, 433, 455 and 482 already carried "REPLACED by section 17.11" when I started (search: `arch-search.log`; today's numbers 49, 154, 230, 301, 357, 371, 435, 457, 484, each +1 after my insert at line 24). Marked now (diff: `arch.diff`, lines cut to 120 characters):
- Line 23 (block diagram, "no record button (17.11)"): note line added under it, line 24.
- Old 343 (zone table, "record switch on the +Y edge at X -5"), old 346 ("notch ... at the record switch"), old 514 (S16 "record switch"), old 515 (S17 "the record pill"): the mark "REPLACED by section 17.11 (record button removed; one control, the joystick)" added inside the cell or sentence, text kept (now lines 344, 347, 516, 517).
- Old 364 (heading 16.5 "and record button"): note line under it (now line 366).
Proof: `verify.log` (lines 24, 344, 366, 516 found by grep -n -F). New state: closed.

## Item 61: antenna CHECKLIST.md
The check is `design/mech/antenna/audit.py` (it pulls every number, citation and quote from antenna-study.md and prints the evidence line each matches). Command and result recorded at CHECKLIST.md line 37; `antenna-audit.log` last line: `claims checked: 408; without a match: 0`, exit 0, 0 "NO MATCH" lines. State: closed.

## Item 129: C73 to C79 (new section in bom-notes.md, lines 119 to 129; bom.csv not changed)
C73 value confirmed (datasheet line 810, page 16; lines 14048 to 14050, page 157); rating not confirmed (Murata sheet is an HTML "Not Found" page). C74, C75, C78 confirmed (lines 14052 to 14055; Table 18 lines 3172 to 3177, page 45). C79 confirmed only together with C90 (about 4 uF at 3.0 V alone). C76 and C77 (1.0 nF) NOT confirmed: the datasheet has no 1 nF capacitor and the parts have no part number. State: open (remainder: C76, C77, C73 rating; the lead rules).

## Item 161: supplier package texts
Search (`removed-parts-search.log`): R41, LED1, Q2 are not in parts.csv, placement-final.csv or the fab parts and position lists; netlist.csv line 399 `,U2,A2,LED1,no_connect` is the power chip's pin named LED1, not the removed part.
- READ-FIRST.template.html line 69 (row now "draft: routed, passes its rules check, not built or tested"), 106, 115 (antenna soldered on the board at its hand end corner with a resin corner over it; simulated, not proven), and line 98 (not named by the lead, same fact). Diff: `readfirst.diff`.
- make_one_pager.py lines 68 and 103: "as an option the software (the circuit board is already routed)" and the Chinese twin. Diff: `onepager.diff`.
- One-pager rebuilt with the script header's command on package ring-supplier-package-2026-11-12-97d5da6 (`onepager-build.log`, exit 0); old PDF saved as `one-pager.before.pdf`; new file ROOT/supplier-package/ring-recorder-one-pager-EN-ZH.pdf. Package folders and zips not rebuilt, so they still carry the old cover page.
State: closed.

## Stale rows 10, 122, 123, 124
- 10: closed (assembly.md line 380, placement-final.csv line 83).
- 122: `check_assembly.log` (exit 1, last line `RESULT FAIL A1, T1`): A2 PASS (line 7); A1 names only `side_slit_seal(SEAL3)` (line 6): the model helper's new row of design/mech/thin/placement.csv, not item 122 (U11, C83 to C88, SEAL1 are no longer named). T1 FAIL (26 of 154 citations) is only line numbers of that file under rewrite. State: closed for the item's parts, with that remainder named.
- 123: closed (assembly.md line 295 FACTORY_EXIT first; line 403 step 2 lists U11, C83, C84).
- 124: stays open: rows 2 and 3 of assembly.md section 6 (line 401; bom.csv line 58 still reads "frame on the liner"); bom.csv is the lead's.

## deferred-triage.csv
`verify.log`: 164 lines (163 rows + header), 6 fields each, other columns changed 0, CRLF 164 and LF 164, state changed in 8 rows (10, 61, 122, 123, 124, 129, 158, 161). Read-only `git diff --stat` (`gitdiffstat.log`): 1 file changed, 8 insertions, 8 deletions. Last line of verify.log: `closed rows 6, not found 0` (22 quotes, all found).

## Checks (own run, after all edits)
- check_docs.py: exit 0, last line `RESULT PASS` (`check_docs.log`).
- firmware-check.py: exit 0, last line `0 failures` (`firmware-check.log`).
- check_bom.py: exit 1, `failures 3`, all three are the model helper's: FOAM1 (line 60), SEAL3, body.md motor angle at US 9 (`check_bom.log`).

## For the lead
1. firmware.md row H19 (line 1200) still says open; assembly steps 25 and 2 are done.
2. READ-FIRST.template.html line 57 still says "six-layer board ... 0.3 mm thick"; stackup.txt shows four layers (L1 to L4). Not changed (not named).
3. Supplier package folders and zips (built 12 Nov) carry the old READ-FIRST; the explorer copies of make_one_pager.py and READ-FIRST hold the old text.
4. bom.csv: no floor slot sealant row and no SEAL3 row; DAM1 line 58 says "frame on the liner" (item 124 rows 2 and 3); C76 and C77 have no part number.
5. guide-joints-notes.md line 72 says check_assembly.py passes; today it fails A1 (SEAL3) and T1.
6. The one-pager PDF at ROOT/supplier-package/ is replaced in place; commit it if tracked.

questions_for_owner: none

RESULT: done, 6 rows closed with grep-verified file and line (10, 61, 122, 123, 158, 161); 124 and 129 stay open with their exact remainder.
