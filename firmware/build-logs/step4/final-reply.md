Step 4 is done: the bar command ran in my own run and ended with `RESULT PASS`, exit code 0, all 20 stages exit 0.
Log: firmware/build-logs/20261112-115540-os-screens.log. Notes: firmware/docs/screens-notes.md (bar a to f one by one, with file, line and log line). I ran no git.

- LVGL on a memory display gave its first frame about 20 minutes into the work (gate of ruling 2). Library kept.
- a. 21 pictures drawn by the screen code, read back from the frame the display driver received, saved as 240x120 PNG with a 4x copy. The manifest names the scene of each one. Copies are in design/software/os/screens/ (42 PNG and manifest.md; sha256 equal to the server). The simulated chip made the same 42 files.
- b. Every scene checks pixels (red dot, passkey digits that change with the passkey, menu highlight that moves with Down, and others): suite screens_draw, pass = 10, total = 10.
- c. The pure table: 112 rows, every action of every screen, plus the lock, double press, long press and session cases: suite screens_table, pass = 23, total = 23, on native_sim and on nrf54lm20bsim.
- d. The two-device test with the step 3 stand-in: pairing from the screen, the notification shows in the list (state and frame hash differ from the empty list), the dismiss chosen on the detail screen arrives as the negative action. `TEST S RESULT PASS (33 checks passed)`.
- e. 12 broken copies fail on their own named check. Two are the R-SIGN copies (rsign_dark on both boards, rsign_blank_panel).
- f. Kit build with the screens: 518,052 bytes of flash (53.15 percent) and 197,584 bytes of RAM (37.76 percent); the step 3 report gave 186,232 and 51,264.

For the lead to decide (notes section 4):
1. The notification list and detail are not in firmware.md 3.3 or 2.2. I put the list on Up from the status screen (2.2 says Up is none there).
2. ring_devices (`rdev_list_add`, rdev_logic.c:63) makes every newly paired device active, against 3.4. The screens put the old one back. The real fix is in ring_devices.
3. The screens store the lock fact in the core's `screen_on`: true when the screen is fully lit or a session is open. This is how the lock and the session exception work. I added `after`, `rglue_event` and `rglue_set_vibration` to ring_glue. No other module was changed.
Also: 3.3 says portrait; the picture is landscape as ruled. The Media screen does not call `rip_media_command`, because 7.6 keeps the keyboard keys and a second send would double each action.

Not built or not proven: the panel driver, the recorder, battery and storage data, the live waveform (it is a drawn line set), and device names from Bluetooth. Nothing ran on real hardware. The three-hour limit was passed while I wrote the notes. The final audit script covers only the claims in this reply and the notes (audit-output.txt).

RESULT: done, no commit (the lead commits), build_all exit 0
