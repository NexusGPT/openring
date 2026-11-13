# Models of the circuit bench: where each one comes from

Written 2026-11-13. "Own model" means the file is ours and its first line says so; every number in it carries its datasheet page in a comment beside it. A maker's file is kept unchanged with its source address.

## Maker models fetched (kept unchanged, not used by the bench)

TI publishes PSpice models for some of its parts. Each file below was fetched from TI's own site with `curl` (no login, no form, no name in the request), unzipped, and the `.lib` copied here unchanged. ngspice (version 45.2 inside KiCad 10.0.8) could not run them. The trials are saved in `design/sim/circuit/logs/ti_tps2553_model_trial.out` and `design/sim/circuit/logs/ti_model_trials/` (a conversion script of ours, `convert_pspice.py`, which turned the PSpice forms into ngspice forms, got the TLV75530P model to parse but not to find a starting point; the TPS2553 model parsed after the conversion and gave a switch that never turned on). The bench therefore uses its own models for these parts and says so.

| File here | Part | Source address | What happened |
|---|---|---|---|
| `tps2553_trans.lib` | TPS2553 (case U5) | https://www.ti.com/lit/zip/SLVM425 (TI product page https://www.ti.com/product/TPS2553, "PSpice transient model") | ngspice stops on the PSpice double braces; after conversion the output stays at 0 V (trial logged). Not used |
| `tps63802_trans.lib` | TPS63802 (case U3) | https://www.ti.com/lit/zip/SLVMCX1 (page https://www.ti.com/product/TPS63802) | same PSpice forms; not run (the TPS2553 and TLV75530P trials already showed the conversion does not reach a working model). Not used |
| `tlv75530p_trans.lib` | TLV75530P (ring U11), the maker's unencrypted model | https://www.ti.com/lit/zip/SBVM833 (page https://www.ti.com/product/TLV755P, "TLV75530P Unencrypted PSpice Transient Model") | parsed after conversion, no operating point found (trial logged in `logs/ti_model_trials/`). Not used |

Fetched and not kept in `models/` (kept inside `work/dl/extracted_ti_downloads.tar.gz` and as zips in `work/dl/`): the TPS2553 TINA model (encrypted), the TLV75511P and TLV755185P models (other output voltages of the same family, not our part), the TPD4E05U06 IBIS file (https://www.ti.com/lit/zip/SLVM741, an IBIS file, not a SPICE model) and the S-parameter file (https://www.ti.com/lit/zip/SLVMBU0), the BQ25895 calculation spreadsheet (https://www.ti.com/lit/zip/SLURAX7, a spreadsheet, not a model). No SPICE model of the BQ25895, the SN74AXC4T774 or the nPM1304 is public on the maker's site (the TI product pages list none; Nordic publishes none).

## Own models used by the bench

| File | Part (reference) | Built from | Notes |
|---|---|---|---|
| `npm1304.lib` | Nordic nPM1304 (ring U2) | nPM1304 datasheet v1.0 (`design/datasheets/npm1304_datasheet_v1_0.pdf`), pages named in the file: VBUS valid thresholds and RON p17, VBUSOUT p17, charger p24 and p29 (ICHG, VTERM, ITERM, VRECHARGE, trickle), battery limit IBATLIM 100 mA p29, RONCHARGER p29, VSET resistor tables p43, BUCK output accuracy, VSYSMIN, drop-out, tSTRT, IOUT p45, power-fail threshold p109, load switch RON, soft start, tSS and RLSPD p69, p77 | behavioural; regulators are ideal sources with the stated current figure; no ripple, no switching, no power-up order beyond what the pages state (both bucks start together, 1.2 ms ramp, p45) |
| `tlv755p30.lib` | TI TLV75530P (ring U11) | TLV755P datasheet SBVS320D (`design/datasheets/motor_tlv755p.pdf`): output accuracy, load regulation, ICL, ISC, ground and shutdown current p5; dropout, UVLO, EN thresholds, start-up time, pull-down p6 | dropout resistance 0.65 ohm is a MODEL CHOICE (the sheet gives only the 500 mA point, 325 mV max) |
| `tpd4e05u06.lib` | TI TPD4E05U06 (ring U9, case U6) | `design/datasheets/codes_tpd4e05u06.pdf`: stand-off 5.5 V, breakdown 6.5 to 8.5 V, leakage 10 nA max at 2.5 V, capacitance 0.42 to 0.5 pF, dynamic resistance 0.8 ohm (lines of `src/codes_tpd4e05u06.txt`) | |
| `sn74axc4t774.lib` | TI SN74AXC4T774 (ring U10) | `design/datasheets/w1_ti_sn74axc4t774.pdf` (SCES898C): input thresholds p5, output levels p6, leakage p6, isolation below 100 mV (quoted in `design/ecad/ring/sch-notes.md` 11.3) | output impedance 57 ohm is a MODEL CHOICE from four VOH and VOL points of p6 |
| `csnp32gcr01.lib` | CS CSNP32GCR01-BOW (ring U3) | `design/datasheets/slim2_cs-sdnand-20230403.pdf` p4 and p8: supply, VIL, VIH, VOL, VOH, leakage, standby current | DC data only; no protocol, no timing |
| `tps2553.lib` | TI TPS2553 (case U5) | `design/datasheets/case_tps2553.pdf` p6 (rDS(on)) and p16 to p17 (current limit equations) | the limit is a hard clamp; no thermal cycling |
| `bq25895_boost.lib` | TI BQ25895 boost mode (case U2) | `design/datasheets/case_bq25895.pdf` p9 (boost accuracy, battery exit voltage), p42 (BOOSTV default), p1 (efficiency) | boost mode only; the charger and the TS comparators are written in the decks of case tests 2 and 3 from the register defaults and the threshold percentages |
| (in `case_decks.py`) | LED1 Kingbright APTF1616 | `design/datasheets/case_kb_aptf1616.pdf` forward voltages at 20 mA | exponential diode with ideality factor swept 2 to 4 (own assumption) |
| (in `make_decks.py`) | BT1 cell (ring) | `design/mfg/specs/cell.md`: capacity per ring size (read from `parts.csv`), charge 4.35 V, peak discharge | open-circuit voltage and series resistance are test parameters; no file states the resistance |
| (in `make_decks.py`) | M1 motor | Jinlong W0525AB001D spec p6: 3.0 V, 80 mA running, 175 mA at start | resistance model; start time 10 ms is an ESTIMATE of `motor-drive.md` line 153 |
