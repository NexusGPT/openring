Step 3 is done: `sh firmware/tools/remote.sh os-iphone "tools/build_all.sh"` ended `RESULT PASS`, `# remote exit code: 0`, and all 14 stages ended with exit 0. Log: `firmware/build-logs/step3/20261111-235859-os-iphone.log`. Notes: `firmware/docs/iphone-notes.md` (bar a to k with file:line and LOG:n, deviations, unproven list, the text for section 7.6, last line `RESULT: done`). I ran no git; nothing is committed.

Built, all under `firmware/`: modules `ring_inbox`, `ring_time`, `ring_iphone` (pure parts in `modules/ring_iphone/src/ripl.c`, Bluetooth in `modules/ring_iphone/src/rip.c`); the join in `modules/ring_glue/src/rglue.c`, `app/prj.conf`, `app/CMakeLists.txt`; tests `tests/inbox`, `tests/time`, `tests/iphone` (each with a broken-copy script) and `tests/bsim/iphone` (`tests/bsim/iphone/run.sh`, the stand-in iPhone in `tests/bsim/iphone/host_app`, `tests/bsim/iphone/ring_app`, `tests/bsim/iphone/broken_edit.py`). `ring_core`, `ring_devices`, `ring_control` and their tests are untouched.

In the log: stand-in scenarios N, R, P pass with 73, 32 and 19 checks; 13 broken copies each fail on their own named check; the logic suites pass on native_sim and on the ring chip board, with broken copies on both; kit build FLASH 184,932 B (18.97%), RAM 45,196 B (8.64%) (step 2: 168,592 B).

Deviations (notes section 4):
1. The kit's ANCS parser keeps 32 bytes per attribute (`kit/ancs_client.h:50`, `kit/ancs_client.c:479`); the brief needs 48, 48 and 160. I wrote the Data Source parser and the request myself; the kit still does discovery, the Notification Source, perform-action and the Media, Time and GATT-service clients. All kit parts build for the ring chip target.
2. The ring's clock holds the iPhone's local time, not UTC: Current Time gives local time and Local Time Information is not read (FW 9.1 says UTC).
3. Scenario P uses my stand-in in plain mode, not the step 2 host program (its scripts are fixed to its own tests).
4. ATT MTU 247 is set in `app/prj.conf`.

Not proven (section 6): anything on a real iPhone (the replay of held notifications, Removed after a dismiss, fragmentation, time notifications); the day-of-week meaning in the stand-in's time (unverified); Apple's AMS appendix is not saved (ids come from the kit header); database-hash caching; paths no run reaches (fetch timeout, discovery error, ATT error 0xA3).

Earlier looks are all listed in section 7: a start without the execute bit, a 3 s clock skew in my test (test fix), one broken copy unreadable because a raw cut character garbled a `printk` line (test fix), two full runs I stopped myself. Cleanup: my server copies, outputs and run files are removed, no process left (`build-logs/step3/cleanup-final.txt`).
