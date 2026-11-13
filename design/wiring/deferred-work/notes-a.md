# Notes for state-a.csv (27 items of open-a.csv)

Run: 2026-11-13, 12:44 to 12:50 CET (clock from `date`). Repo commit 0fa3549904f2ac1880f0fdc4e5d00f2a736fbe7d (`git log -1`). Files were read from the working tree; `git status` was not checked against that commit.
ROOT = .. File paths in state-a.csv are relative to ROOT.

## Method

1. Read open-a.csv (27 items) and the matching rows of deferred-items.md, then lead-decisions.md (74 lines).
2. For each item, opened the cited lines and grepped the design files for its key words. Every quote in state-a.csv was checked by a script that reads the cited line of the cited file (`verify_state_a.py`, log `<scratch>/verify_run2.log`).
3. The CLOSED TODAY and CONTRADICTED quotes were also grepped with `grep -n -F` in their files (log `<scratch>/grep_closed_contradicted.log`).
4. state-a.csv was written in one batch after all reads, not line by line. Its 27 lines are the result.
5. No browser, no web request, no supplier contact. No existing file was changed. Only state-a.csv and this file were written in the deferred-work folder. The generator and checker scripts and two logs are in the session scratchpad, under <scratch>/.

## Counts per state

- CLOSED TODAY: 2 (items 52, 147)
- CONTRADICTED: 2 (items 71, 121)
- STILL OPEN, OWNER: 1 (item 60)
- STILL OPEN, NEEDS A MAKER OR SUPPLIER: 5 (items 54, 68, 143, 144, 145)
- STILL OPEN, NEEDS HARDWARE: 17 (items 42, 43, 57, 58, 59, 66, 75, 79, 86, 87, 93, 94, 142, 146, 150, 151, 159)
- STILL OPEN, DESIGN WORK: 0
- Total: 27 of 27

## First verification run found 8 errors, all in my own file paths

The first run of `verify_state_a.py` reported 8 failures: requirements.md was written as design/requirements.md (the file is at ROOT/requirements.md). I fixed the generator and regenerated the file. The final run reports `FAILS 0`, and that is the result reported here. The 8 failures were not quote errors.

## Things that do not match the deferred-items.md brief

- Item 52 and item 147: the light the items describe was removed in v7. architecture.md line 523 (row S25) says so, and requirements.md line 205 records the removal. light-path.md line 111 is stale. Lead-decisions row 40 already asks for its text pass.
- Item 71: requirements.md line 195 uses old cell sizes (20.4 to 27.2 mAh). cell.md line 63 uses the per-size values. The two files disagree.
- Item 121: requirements.md line 26 says S6 is a goal. Line 204 says the target stays IP65. The lead decision in lead-decisions.md line 64 follows line 26. Line 204 is not corrected.
- Item 151: the quote "Aina publishes no weight" that the brief cites at requirements.md line 25 is gone. Line 25 now holds the owner's decision for S5, so S5 is closed. A4, A8, P7 and D3 remain bench items.
- Item 159: the VBUS question on firmware-f5-notes.md line 81 is answered by wiring/w7-facts.md line 135 (VBUSOUT is a separate output). The netlist connects VBUSOUT only to C73 and U2 pin C3 (ecad/ring/netlist.csv lines 305 and 306, not quoted). The remaining sub-items stay open.
- Stale line citations in deferred-items.md: item 87 cites case-architecture.md line 220, which does not hold the 1.97 mm figure (it is at line 235). Item 93 cites case-notes.md line 113, which is the magnets row. The quote is at line 122. Item 94 cites the C4 note in case/look; the same words are in case-notes.md line 72.
- Item 52 cites architecture.md line 695, which sits in section 17.21. Line 523 marks that text as do not use.
- Item 66 cites lead-decisions row 17, which moves the currents to the build guide. It does not give a value.

## Not checked, and why

- Item 66 asks whether a maker document closes the main chip, radio and power chip currents. design/datasheets holds nrf54lm20a_szlcsc.pdf, nrf54lm20x_caaa_ref_pcb_0_2.pdf and mcu_nrf54l15_ds_v2.2.pdf. I did not open them, so I have not tested whether they give these currents. The state uses lead-decisions row 17 (measure in the build guide).
- Items 54 and 145: the maker answers are missing from the files I read (architecture.md line 870; cell.md line 93). I searched only the files named in the brief and the files they cite, not other folders of the repo.
- No line under */evidence/, */out/, */*-work/ or design/case/look/ is cited in state-a.csv. design/case/look/c4_case-notes.md line 92 and old_C5 say 360 gf, a history value. The current case-notes.md line 122 says 159 gf.

## Odd things in the inputs

- lead-decisions.md is in date order, oldest row first. The standing rule says newest row first. I took "newest" from the date column.

RESULT: done, 27 of 27 items have a line: 2 CLOSED TODAY, 2 CONTRADICTED, 17 STILL OPEN NEEDS HARDWARE, 5 STILL OPEN NEEDS A MAKER OR SUPPLIER, 1 STILL OPEN OWNER, 0 STILL OPEN DESIGN WORK.
