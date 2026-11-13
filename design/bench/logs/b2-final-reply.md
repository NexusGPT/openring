RESULT: done, bench plan B2 written; check_bench.py prints RESULT PASS on B2 and RESULT FAIL on B1 and on the faulty copy.

Files (all in design/bench/): bench-plan.md (B2), bench-plan-B1.md (B1, unchanged), bench-kits.md, check_bench.py, bench-plan-faulty.md, b2-notes.md, logs/, sources/. Every file I wrote is in design/bench/ (logs/bench_listing.log).

Check (python3 -I check_bench.py <plan> design/bom.csv, logs in logs/check_FINAL_*.log):
- bench-plan.md: rules passed 4 of 4, RESULT PASS (exit 0)
- bench-plan-B1.md: rules passed 0 of 4, RESULT FAIL (exit 1)
- bench-plan-faulty.md (microphone part changed to IM68D128BV01): rules passed 2 of 4, RESULT FAIL
- extra copies, both RESULT FAIL: recording light named as current; empty pass line.
Two earlier runs are reported in b2-notes.md section 3: B2 first failed because rule R2 matched file names (fixed in the check), and an earlier version of rule R3 gave 3 false hits on B1 (question id Q2; narrowed, all runs repeated; the raw log of that run was overwritten, logs/repro_r3_v1_on_B1.log reproduces it).

What B2 does: parts follow the ring: nPM1304 EK (nPM1304-EK), the ring's own Knowles SPK0641HT4H-1 microphones and Jinlong W0525AB001D motor, motor regulator TLV75530PDQNR, Adafruit 504 5-way switch (centre = record control), Waveshare 10507 OLED as the screen stand-in, Adafruit 254 storage plus two Adafruit 395 level converters. The recording light is out of wiring and tests. New test T4: the screen as the recording sign (VDD_MIC rises only after the red-dot frame; forced draw failure leaves VDD_MIC off; camera frames between VDD_MIC on and off all show the dot). Tests T0 to T7 (8) each carry a pass line with file, section and a verbatim quote that the check verifies. T2 states 4.1 mA as today's figure (firmware.md 8.5), says the always-lit sign has no measured figure, and measures it as I(S1) minus I(S0).
Wiring table: 43 rows, pin to pin with the ring's net names; DK header pins read from the saved DK schematic.

Order codes: 8 confirmed with their source file; 3 not confirmed: Knowles SPK0641HT4H-1 (no seller code, no maker evaluation board found), Jinlong W0525AB001D, Plaud NotePin. Distributor and Nordic pages answered 403, bot pages or no reply; none was worked around (logs/fetch_all.log).

Needs you or a person with a browser: the nPM1304 EK user guide (battery connector polarity, header labels, VDDIO, pull-ups) is behind a browser check, so the EK side is wired by PMIC pin and ball (plan section 9). Owner questions: accept the DK's B die with the A rules in software; Plaud Note Pro (requirements.md) or NotePin.

Cannot be proven on the bench (b2-notes.md section 4): the ring's panel current and start-up, the panel supply really switching off, the one-way level shifter U10, charging at 4.35 V, switch feel, the sound path, the A die.
