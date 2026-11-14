# Brief: step 7 fix round 1 (lead, 2026-11-13 night)

Goal: Close the findings of the independent review of step 7 (firmware/docs/step7-review.md, verdict FAIL: 2 major, 5 minor, 2 notes) and make the power part's real file compile for the ring board. Read the review in full first.

FW: firmware
Version: project commit 47204f09 plus your own notes file. The lead's own full run of 47204f09 (name lead-full5) is running on the server in its own copy /root/ring-os/src-lead7: leave it alone.

The lead's rulings, one per finding:
- S7-01 (netlist copy can drift): (a) tools/remote.sh compares firmware/boards/ringrec/netlist.csv with design/ecad/ring/netlist.csv before it copies anything, when the design file exists two folders above firmware, and refuses to run when they differ, printing both sha256; in an export that holds only firmware/ it says in one line that the comparison was skipped. (b) the ring-pins stage prints the copy's sha256 and a line that says where the comparison happened. (c) a self test you run and log: change one row of a scratch copy, show the refusal. Do not weaken remote.sh's existing rules.
- S7-02 (SD_CS while VDD_SD is off, design/firmware.md l.506): the card's chip-select line must be an input with no pull whenever VDD_SD is off, and driven again before VDD_SD comes on. Find out from the SDK's own source in the container what the SPI driver and the disk driver do with a cs-gpios line on suspend; then make it true in the place that switches VDD_SD (the storage part's real file modules/ring_store/src/rst_hw_real.c, or the board's pin states if that is enough), and correct the comment at pinctrl.dtsi line 23. State plainly what is proven by reading and compiling and what only hardware can prove.
- S7-06 and the power part: fix the three fuel gauge calls of modules/ring_power/src/rpw_hw_real.c (lines 307, 309, 310) to the SDK 3.4.2 library's real signatures, read from its header in the container (cite file and line); set CONFIG_RING_POWER_REAL=y for the ring board; the ring build must then compile that file with real code and the rail switch must reach the real driver. If another real file needs a matching change, make it and list it. The simulated tests must stay as they are and pass.
- S7-03 and S7-04 (the pin check): compare GPIO flags too (pull-ups of the joystick switches, active level of MOTOR and of every enable pin, against design/firmware.md and the netlist's notes; where no source states the flag, print "no source" and do not invent one); read the fixed-function pins from the devicetree where the devicetree states them, else say "from the chip's fixed function" per pin; fail on a property the reverse scan cannot parse. Add broken copies: a wrong port, a removed or disabled node, an extra pin, an unknown net, a changed netlist row, a wrong flag. Each must fail on its own signal only. Correct board-notes.md line 189 to what the check sees.
- S7-05: correct README.md line 96.
- S7-07: say in README.md and board-notes.md that MCUboot is signed with the SDK's debug key, NOT FOR SHIPPING, and that the production key is made at the factory step; change no key.
- S7-08 and S7-09: no code change; S7-09 see "production setting" below.

The lead's rulings on your open choices:
- Settings back end: ZMS, accepted.
- MCUboot area: 64 KB as design/firmware.md 9.2 says; write in the notes what the SDK's 62 KB would buy.
- Cell model: Nordic's 20 mAh sample stays as a stand-in, marked NOT THE RING'S CELL in the file's head, the README and the notes.
- Production setting without the debug UART (design/firmware.md l.1061): write it as an extra settings file for the ring board and build it in a new stage (compile only, memory report printed); the development build keeps its console.
- DEVELOP_IN_NRF54LM20B: say in the notes what the option does, from its Kconfig text; leave it off unless the build needs it.
- RAM: no module change in this round. Fill the table "budget line | budget | measured" for the ring build with POWER_REAL on, with the full symbol list this time (the server has room now).
- remote.sh sending the design netlist: no; ruling S7-01 (a) replaces it.
- Joystick key codes: your choice stands; list it in the notes as open for the review of the real joystick driver.

Bar (it can fail):
1. Ring build with CONFIG_RING_POWER_REAL=y: stage ring exit 0; the driver list shows rpw_hw_real.c compiled with real code; flash and RAM lines cited.
2. The pin check passes on the ring build and every broken copy (the old three and the new ones) fails on its own signal only; cite each line.
3. S7-01 self test logged: the refusal line quoted.
4. S7-02: the code or pin state that makes SD_CS an input with no pull while VDD_SD is off, with file and line, and the SDK source lines you read.
5. The whole tools/build_all.sh in your own server copy /root/ring-os/src-s7: last result line RESULT PASS, every stage exit 0 (start it in the background with an exit file, end your turn naming the job; the lead wakes you).
6. docs/board-notes.md gets a section "Fix round 1" with one row per finding: what changed (file:line), the log line that proves it, or "ruled, no change".

Owns: what you owned in step 7, plus for this round only: firmware/modules/ring_power/src/rpw_hw_real.c, firmware/modules/ring_store/src/rst_hw_real.c, firmware/tools/remote.sh (ruling S7-01 only), and a new production settings file under firmware/app/. Any other module file a ruling forces: stop and ask the lead first.
Must not touch: every other module and every test; design/ (read only); the review file and the reviewer's folder; the server copies /root/ring-os/src and /root/ring-os/src-lead7 and the lead's run; other people's processes on the server; any process on the Mac you did not start; any browser. The server's address and the ssh key are never printed or written.
Writes to: firmware/docs/board-notes.md (section "Fix round 1", as you go).
Done when: the lead can read bars 1 to 6 from your full run's log and the notes.

Standing rules: the same as your step 7 brief, word for word (no git at all; never stderr to /dev/null, use 2>&1; absolute paths and chained cd; file names never start with REPORT, SUMMARY, FINDINGS or ANALYSIS; clock times from `date`; no foreground sleep; long runs in the background with an exit file; nothing large on the Mac; every number from a log line you name; no check result written before it is read; remove your own finished run folders on the server through remote.sh's host mode).
Limits: 4 hours of your own work from your first `date` of this round.
End line: the last line of the "Fix round 1" section is `RESULT: <done|blocked>, <one sentence>`.
Your report ends with `questions_for_owner:` (`none` if there are none).
When you finish, your final reply is your report: it reaches the lead automatically. Keep it under 3,500 characters and put anything longer in a file it names. Do not also send it with SendMessage; use SendMessage only for a question or news while you keep working.
