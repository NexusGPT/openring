import re
D=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/bench/")
def lastlines(name,n=2):
    L=open(D+"logs/"+name).read().rstrip("\n").split("\n")
    return L[-n:]
def res(name):
    L=lastlines(name,2); return "%s | %s" % (L[0],L[1])
pass_l=res("check_FINAL_bench-plan.log")
b1_l=res("check_FINAL_bench-plan-B1.log")
f_l=res("check_FINAL_bench-plan-faulty.log")
fl_l=res("check_FINAL_bench-plan-faulty-light.log")
fp_l=res("check_FINAL_bench-plan-faulty-passline.log")
notes=f"""# Bench plan B2: notes (builder, 2026-11-12)

Version: ring files at commit bf21943. Files written: `design/bench/bench-plan.md` (B2), `design/bench/bench-plan-B1.md` (B1, byte-identical to the file before; compare `design/bench/logs/bench-plan-B1-original.md`), `design/bench/bench-kits.md`, `design/bench/check_bench.py`, three faulty copies, logs, saved sources. Every file I wrote is under `design/bench/` (listing in `design/bench/logs/bench_listing.log`).

## 1. Kits and parts changed from B1 to B2, with the source of the new choice

| B1 item | B2 item | Source of the new choice |
|---|---|---|
| nPM1300 EK, NPM1300-EK | nPM1304 EK, nPM1304-EK | design/architecture.md line 644 and 17.13, 17.18; design/bom.csv line 3; design/datasheets/npm1304_datasheet_v1_0.txt Table 50 page 168; review 3 C6 |
| Infineon kit KITIM68D128BV01FLEXTOBO1 (IM68D128B) | Knowles SPK0641HT4H-1, two of the ring's own parts on carrier CB-MIC (no maker evaluation board found) | design/bom.csv line 9; design/architecture.md 17.19; design/mech/mic-path/mic-path.md line 32; review 3 C7 |
| Vybronics VC0720B088L plus Adafruit MOSFET driver 5648 | Jinlong W0525AB001D plus its own regulator TI TLV75530PDQNR on carrier CB-MOT with C83, C84, R61, R62 | design/bom.csv lines 44 to 46 and 62, 63; design/architecture.md 17.16 and 17.22; design/ecad/motor-drive/motor-drive.md sections 2.1, 2.2; review 3 C8 |
| two push buttons ("2-direction thumb control") | Adafruit 5-way navigation switch 504: up, down, left, right and centre; the centre (net BTN_REC) is the record control | design/bom.csv lines 39, 40; design/architecture.md 17.11, 17.29; design/firmware.md sections 2.1, 2.2 |
| no screen on the bench | Waveshare 0.95inch RGB OLED (A), SKU 10507, as the closest kit that shows the recording sign; the ring's panel TOH095XVT-01 joins when its start-up code arrives | design/bom.csv line 10; design/architecture.md 17.30; design/bench/bench-kits.md section 4 |
| recording light wired (3.0 V, 680 ohm, LED, transistor on VDD_MIC), 1 red LED, 680 ohm resistor in the small parts, light test in Q3 | all removed from wiring, parts and tests; replaced by test T4 (screen as the recording sign) | design/architecture.md 17.30, 17.31; design/firmware.md 3.2 (R-SIGN, SIGN-1) and 9.3 (T-SIGN) |
| Adafruit microSD breakout 254 | kept; two Adafruit 395 TXB0108 converters added (storage lines and screen lines, because the DK's I/O rail is 1.8 V and both breakouts need 3.3 V logic) | design/bom.csv line 7; design/bench/sources/dk_sch_p6-06.png; design/bench/sources/adafruit_254.txt, adafruit_395.txt |
| SparkFun 40 mAh cell PRT-13852 | removed; the Power Profiler Kit II stands in for the cell (a 3.70 V cell cannot take the ring's 4.35 V setting) | design/bom.csv line 47; design/bench/bench-kits.md section 7 of B1 (copy in design/bench/logs/bench-kits-B1-copy.md) |
| nRF54LM20 DK, one PPK2, Plaud NotePin | kept; the DK is built for board target nrf54lm20dk/nrf54lm20a/cpuapp; the PPK2 is used in two runs (T2) | design/bench/sources/zephyr_nrf54lm20dk_board.txt |
| Q1 to Q3 with pass lines written in the plan | tests T0 to T7; every pass line has a design file and section and a verbatim quote checked by check_bench.py | plan section 5 |
| recording current pass line 4.0 mA | the figure the design uses today, 4.1 mA from the cell (design/firmware.md 8.5, architecture 17.26); the always-lit sign has no measured figure; test T2 measures it as I(S1) minus I(S0) and I(S2) minus I(S0) | design/firmware.md 8.5 and 3.2; review 3 C17 |

B1 price total (313.66) is not recomputed for B2: the nPM1304 EK, Knowles, Jinlong and TLV75530 prices were not read (see the web record in section 5).

## 2. Order codes (status in the plan, section 2, column Status)

Confirmed (8): NRF54LM20-DK (design/bench/bench-kits.md section 1); nRF-PPK2 (design/bench/bench-kits.md section 1); nPM1304-EK (design/datasheets/npm1304_datasheet_v1_0.txt, Table 50 page 168); TLV75530PDQNR (design/ecad/motor-drive/src_tlv755p.txt, order line); Adafruit 504 (design/bench/sources/adafruit_504.txt, read 2026-11-11 23:31 UTC); Waveshare 10507 (design/bench/sources/waveshare_oled095_a.txt, same time); Adafruit 254 (design/bench/sources/adafruit_254.txt, same time); Adafruit 395 (design/bench/sources/adafruit_395.txt, same time). check_bench.py reads each code in its cited source file.

Not confirmed (3): Knowles SPK0641HT4H-1 (no seller code: reel suffix and distributor code unknown, mic-path.md line 32; searches in design/bench/logs/fetch_all.log); Jinlong W0525AB001D (bom.csv line 44: the maker must confirm the part and its price); Plaud NotePin (no code on the saved page copy, bench-kits.md section 8).

Also written "not confirmed" in the plan section 9: the label of each EK header and the EK's battery connector polarity (user guide behind a browser check), the PPK2 header names, the SDK sample names, the Plaud export format.

## 3. The check's three log lines (and the extra copies)

check_bench.py was run as `python3 -I check_bench.py <plan> design/bom.csv`; each log is in `design/bench/logs/`.

- `check_FINAL_bench-plan.log` (B2): {pass_l}
- `check_FINAL_bench-plan-B1.log` (B1): {b1_l}
- `check_FINAL_bench-plan-faulty.log` (B2 with the microphone ring part changed to IM68D128BV01): {f_l}
- extra: `check_FINAL_bench-plan-faulty-light.log` (a wiring row naming the recording light as current): {fl_l}
- extra: `check_FINAL_bench-plan-faulty-passline.log` (the pass line of T6 emptied): {fp_l}

The rules: R1 parts map against bom.csv (reference and part number); R2 every power chip, microphone, motor and screen part number in the text is held by bom.csv or is a confirmed kit code; R3 no line names the recording light as current; R4 every test has a pass line, an existing source file and section, and quotes that are found verbatim in that file.

Earlier runs, all kept in `design/bench/logs/` (result of each against `expected_results.txt`):
- `check_run0_b2_first.log`: B2 FAIL, expected PASS. R2 matched file names with underscores. Cause fixed in check_bench.py (token class).
- `check_run1_b2.log`: B2 after that fix, PASS.
- A first set of per-plan logs named `check_final_*.log` (check version 1, all five plans) was overwritten by the final set `check_FINAL_*.log`: the file system ignores letter case, so both names are one file. That raw output is lost. What it showed for B1 is reproduced by `repro_r3_v1_on_B1.log` (rule R3 of version 1 on B1: hits on lines 12, 13, 22, 31, 50, 54, 64; lines 12, 22 and 54 are the question id Q2 of B1's current question, a false hit of the bare pattern Q2 that differed from the expectation of 13, 31, 50 in `expected_results.txt`; line 64 was a real light line missing from that expectation). Rule R3 was then changed: Q2 counts only with transistor, gate, LED or light on the line.
- `check_v2_*.log`: after the R3 change; `check_v3_bench-plan.log`: after a later edit of the T2 pass line; the faulty copies and `check_FINAL_*.log` were then made again from the final plan and run again. `final_hashes.log` holds the hashes of the delivered plan, check and B1.
- The check cannot see whether a pass line is right, only that it is sourced: R4 compares quotes with the cited files, and the plan's pass-line wording around them is mine where it says [CHOICE].

Audit: `design/bench/logs/audit_b2.py` pulls the paths, dates, numbers, codes and counts out of this file and out of the final reply by itself and prints the saved line each matches (`logs/final_audit.log`). Its matching of plain numbers is loose (the first saved file that holds the same number); the statements about counts, check results, earlier runs and the web log have their own checks in the same script. `logs/final_audit_run1.log` is an earlier run of it that failed one statement check (the lost version-1 log, section 3); it was fixed with `repro_r3_v1_on_B1.log` and the audit run again.

## 4. What the bench still cannot prove

1. The ring's panel: the current of the always-lit red dot and timer, and the SH8501A start-up; the stand-in is an SSD1331 OLED at 96 x 64. T2 and T4 must be repeated on the TOH095XVT-01 (architecture 12.1, S30).
2. That the panel supply is really off with OLED_PWR_EN low, and a panel failing during use (firmware.md 3.2, "What is lost"): the module has no enable pin; T4 reads the pin only. SIGN-1 is a host test of the firmware (work item W12) and is a prerequisite, not part of the bench.
3. The ring's one-way level shifter U10 (Hi-Z below 100 mV on VDD_SD, review F07) and the SD NAND CSNP32GCR01-BOW: the bench has a microSD card behind two TXB0108 converters.
4. The recording current is a sum of two runs (T2: R-A at the EK battery input, R-B at the DK header P14, converted at the design's 90 percent); the buck's real efficiency at the ring's load is not measured.
5. Charging at 15 mA to 4.35 V, the cell's discharge limit and its protection circuit (S12): there is no cell on the bench.
6. The feel, force and travel of the ring's switches and cap, and the ring's switch land pattern (S9, B9); the 5-way switch is a stand-in.
7. The sound path through the housing floor (B7), antenna, size, weight and the three hand positions of the requirement.
8. The nRF54LM20A die itself (the DK has the B die with the A rules in software); the ring's rail arrangement (the DK keeps its own power chip).
9. Wiring on the EK side is given by PMIC pin and ball, because the nPM1304 EK user guide could not be read: the EK's header labels, battery connector polarity, VDDIO source and pull-ups are unconfirmed (plan section 9).
10. Prices and stock of the nPM1304 EK, Knowles SPK0641HT4H-1, Jinlong W0525AB001D and TLV75530PDQNR: not read.

## 5. Web record

Pages were fetched as text with curl, read only: no account, cart, sign-up or contact, and no project, owner or company name in any request. Log of each request: `design/bench/logs/fetch_all.log` (UTC time, status, bytes, URL); the first request, to the Nordic DK guide, is in `design/bench/logs/fetch_nordic_dk_connector_if.log` and used the generic user agent string 'Mozilla/5.0 (compatible; text-fetch)'; all later ones used the default curl agent. Refused with a browser check or bot check and not worked around: Nordic (docs and product pages), Digi-Key, TME, Octopart (HTTP 403), a search engine (HTTP 202 bot page), Knowles site search (bot page). No reply: Mouser, Arrow, Newark, Farnell (curl errors 92 and 28, 56). Read: Zephyr documentation and sources (board, shield), Adafruit 254, 395, 504, 684, 367, 1010, 1119, 3101, Waveshare 10507, TI TLV755P page, the Alps SKQUCAA010 sheet. DK schematic pages 4, 6 and 8 were rendered from the saved PDF (`design/bench/sources/dk_sch_*.png`).

RESULT: done, bench plan B2 follows the current ring (nPM1304 EK, Knowles microphones, Jinlong motor on its TLV75530 regulator, 5-way switch, OLED stand-in, test T4 of the screen sign) and check_bench.py prints RESULT PASS on B2 and RESULT FAIL on B1 and on the faulty copy; 3 order codes stay not confirmed and the nPM1304 EK pinout was not readable.
"""
open(D+"b2-notes.md","w").write(notes)
print(len(notes))
