# Brief: step 7 fix round 3 (lead, 2026-11-14 morning): one mechanism, not a third patch

Why this round is different. Three reviews failed step 7 on the same rule of design/firmware.md l.506 ("no storage line is driven high while VDD_SD is off"), each on another path: S7-02 (suspend), S7R-01 (boot), S7T-01 (a failed first init). Majors open after each review: 2, 1, 1. The lead's step back: the fault class has one cause. The lines' safe state was tied to the bus driver's life (suspended or not, initialised or not, `bus_up`), so every path that changes the driver's state needed its own patch. From now on the safe state is tied to the SUPPLY: one function makes the four card lines safe, with no condition, and it runs on every way to "VDD_SD off".

Read first, in full: firmware/docs/step7-review-3.md (findings S7T-01 to S7T-06).

FW: firmware
Version: project commit 8bb60559.

The lead's rulings:
1. S7T-01, the mechanism. In firmware/modules/ring_store/src/rst_hw_real.c write ONE function (call it `lines_safe`) that, without reading `bus_up` or any device state: (a) configures SD_CS as disconnected (input buffer off, no pull) through the GPIO API on the cs-gpios spec; (b) applies spi00's "sleep" pin state directly with the pin control API on spi00's own pin configuration (not through the SPI driver's suspend), so SD_SCK, SD_MOSI and SD_MISO are inputs with no pull; both must be legal whether spi00 was never initialised, is active, is suspended, or failed its init. The hook the storage part calls before VDD_SD goes off (`b_suspend`) ALWAYS ends by calling it, on every return path, error returns included; so does every failure exit of the first init and of resume. The driver's own suspend still runs first when the bus is up (so the driver's state stays right); `lines_safe` then runs after it regardless. If the pin control API cannot be used on a deferred, never-initialised spi00 (read the SDK source: PINCTRL_DT_DEV_CONFIG_GET needs only the devicetree, not the device), say exactly why with the source lines and stop for the lead.
   Then prove the rule once, by structure, not by path: list every place in firmware/modules/ring_store/src/rst.c and in the power path where VDD_SD can go off (read only; rst.c is not yours), and show each is preceded by the hook. If one way to "VDD_SD off" does not pass the hook (ship mode, a fault path, the power part switching the rail itself), report it to the lead with file and line: do not patch rst.c.
2. S7T-02: after the first-init loop, all three devices must answer device_is_ready(); else the function returns an error, `bus_up` stays false and `lines_safe` runs. Read and cite what device_init returns for a device whose earlier init failed.
3. A test that can fail, without hardware: a unit test is not possible for the real file, so add to the ring stages a static check (in tools/build_all.sh, with a planted copy that fails): every `return` of `b_suspend` and every failure exit of the first init and of resume in rst_hw_real.c goes through `lines_safe` (for example the hook's body is one wrapper `int r = suspend_inner(); int s = lines_safe(); return r ? r : s;`, and the check asserts that shape). Keep it simple and honest: say what the check sees and what it does not.
4. S7T-03: write the section "Fix round 2 and 3" in docs/board-notes.md: one row per finding S7R-01 to S7R-09 and S7T-01 to S7T-06; the step-by-step account of the card's four lines from reset to the first power-on and through one power-off, with the source line of each step; the list of what hardware must prove; the pin check's remaining blind spots; the RESULT line.
5. S7T-04: plant the path that replaced the "uart20 enabled" test, and make the pull-down self test match the whole property, not a substring.
6. S7T-05: the comment at modules/ring_rhw/include/ring_rhw/rhw.h line 97 still calls the sign open: report the corrected wording to the lead (that header is not yours; the lead changes it).
7. S7T-06: nothing for you; the lead saves the logs and removes the reviewer's scratch copy.

Proof for this round (targeted, not the whole build): run only the stages the change can reach, in your own server copy /root/ring-os/src-s7, with your stage-only command (as stages7f2.cmd): dk, ring, ring-drivers, ring-ram, ring-pins, ring-pins-broken, ring-production, ring-production-check, ring-production-broken, plus the new static check and its planted copy. The lead runs the whole tools/build_all.sh once on your result; a fourth reviewer reads the diff.

Bar (it can fail):
1. `lines_safe` exists as ruled; the hook and the failure exits always pass it (file:line for each).
2. The list of every way to "VDD_SD off" with the hook before it, or the reported exceptions.
3. The static check passes and its planted copy fails (log lines).
4. The targeted stages all exit 0 (log cited); the ring build compiles rst_hw_real.c with real code.
5. The notes section of ruling 4 is written.

Owns: firmware/modules/ring_store/src/rst_hw_real.c, firmware/tools/build_all.sh, firmware/tools/check_ring_pins.py (ruling 5 only), firmware/docs/board-notes.md, the board folder if ruling 1 needs a pin state, and a new folder firmware/build-logs/step7/fix3.
Must not touch: every other module file (rst.c and rhw.h included) and every test; design/; the three review files and the reviewers' folders; the server copies /root/ring-os/src and /root/ring-os/src-lead7; other people's processes on the server; any process on the Mac you did not start; any browser. The server's address and the ssh key are never printed or written.
Writes to: firmware/docs/board-notes.md (as you go: write the notes section FIRST from what you already know of round 2, then add round 3; your last turn was cut by a usage limit before any notes were on disk).

Standing rules: the same as your step 7 brief, word for word (no git at all; never stderr to /dev/null, use 2>&1; absolute paths and chained cd; file names never start with REPORT, SUMMARY, FINDINGS or ANALYSIS; clock times from `date`; no foreground sleep; runs over two minutes in the background with an exit file, then end your turn naming the job; nothing large on the Mac; every number from a log line you name; no check result written before it is read; remove your own finished run folders on the server).
Limits: 90 minutes of your own work from your first `date` of this round.
End line: the last line of the notes section is `RESULT: <done|blocked>, <one sentence>`.
Your report ends with `questions_for_owner:` (`none` if there are none).
When you finish, your final reply is your report: it reaches the lead automatically. Keep it under 3,500 characters and put anything longer in a file it names. Do not also send it with SendMessage; use SendMessage only for a question or news while you keep working.
