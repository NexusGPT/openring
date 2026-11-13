# nrf54 pairing probe

Pre-registration, written 2026-11-11 21:12:45 CET before any run of this probe (earlier attempts: docs/devices-control-notes.md section 6.1, build-logs/step2/).

Hypothesis: on the simulated ring chip (board nrf54lm20bsim/nrf54lm20a/cpuapp, BabbleSim), encrypted Bluetooth links fail below our own code.

Pass line (hypothesis holds): Test 1: an UNMODIFIED SDK Bluetooth sample pair that encrypts its link, built for nrf54lm20bsim/nrf54lm20a/cpuapp and run in BabbleSim, ALSO fails to reach an encrypted link on that board (reason 0x3d or another encryption failure) while the same stock pair reaches an encrypted link on nrf52_bsim/native.
Falsifier (fail line): the stock pair reaches an encrypted link on nrf54lm20bsim: then the fault is in our code or configuration, and the first difference I can show is named (configuration option, crypto backend, controller choice).
Test 2, only if test 1 passes the hypothesis: the same stock pair on nrf54l15bsim/nrf54l15/cpuapp.
Spend cap: 90 minutes, 150 tool calls; no paid calls. Server copy: /root/ring-os/src-probe54, removed at the end.
Rules fixed now: a build or run crash, timeout or missing log is recorded as "cannot tell", never as pass or fail. If no stock encrypting sample can be built for the board, result is blocked, naming each attempt.
Writes to: this file.

## Runs

All logs in firmware/build-logs/probe-nrf54/ (written by tools/remote.sh; the exit code is the script's). Server copy /root/ring-os/src-probe54, own BabbleSim dir /ws/out/probe54 (the shared /ws/tools/bsim/bin was not written). SDK nRF Connect SDK 3.4.2 (Zephyr 4.4.2), SoftDevice Controller on all runs (line `bt_sdc_hci_driver: SoftDevice Controller build revision`).

Stock pair: Zephyr's own BabbleSim test tests/bsim/bluetooth/ll/conn built with its stock `compile.source` (conf prj_split.conf), run by its unmodified script tests_scripts/basic_conn_encrypted_split.sh (peripheral + central_encrypted; the central calls bt_conn_set_security(BT_SECURITY_L2); the script passes `-RealEncryption=1` to both devices). Zephyr's own CI lists this script for nrf54l15bsim (tests/bsim/bluetooth/tests.nrf54l15bsim_nrf54l15_cpuapp.txt). Other candidates seen and not used: tests/bsim/bluetooth/host/security/* (platform_allow nrf52_bsim only), sdk-nrf tests/bluetooth/bsim/custom_ltk (not looked at further).

| # | Board | Run | Key log lines | Exit | Log |
|---|---|---|---|---|---|
| 1a | nrf52_bsim/native | stock script, as shipped (RealEncryption=1) | `Updating connection (bonded: 1)` at 1.393892 s; `INFO: Testcase passed` (both devices) | 0 | 20261111-211639-stock-conn-nrf52.log |
| 1b | nrf54lm20bsim/nrf54lm20a/cpuapp | stock script, as shipped (RealEncryption=1) | `Updating connection (bonded: 1)` at 1.397465 s; `INFO: Testcase passed` (both devices); no disconnect | 0 | 20261111-211718-stock-conn-nrf54lm20.log |
| 1c | nrf52_bsim/native | same binaries, script copy WITHOUT `-RealEncryption=1` (BabbleSim default: plain text) | `Updating connection (bonded: 1)`; `INFO: Testcase passed` | 0 | 20261111-211902-plain-nrf52_bs.log |
| 1d | nrf54lm20bsim/nrf54lm20a/cpuapp | same binaries, script copy WITHOUT `-RealEncryption=1` | `Peripheral disconnected (reason 0x3d)` at 1.202890 s; `bt_smp: The in-progress pairing has been deleted!`; central `Disconnected ... (reason 0x08)`; `test_connect1 failed (not passed after 6 seconds)` | 255 | 20261111-212151-plain-nrf54lm2.log |
| 2a | nrf54lm20bsim/nrf54lm20a/cpuapp | OUR control test A, copy of tests/bsim/control/run.sh with `-RealEncryption=1` added to ring and host (diff below) | `TEST A RESULT PASS (76 checks passed)`, `exit codes: phy 0, ring 0, hosts 0` | 0 | 20261111-212403-ctl-realenc-A3.log |

Console copies: console-plain-*.txt, console-ctl-realenc-A3.txt (same content as the logs). Scripts: tests/bsim/probe-nrf54/stock_conn.sh (1a, 1b), stock_conn_plain.sh (1c, 1d), run_ctl_realenc.sh (2a). Copy diff for 2a, made by sed from control/run.sh at the time: HERE fixed to /ws/firmware/tests/bsim/control, OUT under /ws/out/probe54, `-RealEncryption=1` on the ring and host command lines, `LD_LIBRARY_PATH=/ws/tools/bsim/lib` on those two lines (the models look for libCryptov1.so there). control/ was read, not written.

BabbleSim source, read only: /ws/modules/bsim_hw_models/nrf_hw_models/src/HW_models/BLECrypt_if.c lines 107-111: option `RealEncryption`, "(0)/1 Use the real AES encryption for the LL or just send everything in plain text (default)". Our tests/bsim/control/run.sh and the earlier probes in build-logs/step2 never pass this flag (grep of control/ and docs/ for RealEncryption: no hit, search saved in this session's console only, not in a log file).

## Verdict against the pass line

Test 1, as pre-registered (stock script as shipped): the stock pair REACHES an encrypted link on nrf54lm20bsim/nrf54lm20a/cpuapp (run 1b, same result as on nrf52_bsim/native, run 1a). That is the fail line. The hypothesis "encrypted links fail below our own code on that board" is not supported: FAIL. Test 2 not run (its condition, test 1 passing the hypothesis, did not hold).

First difference shown (the fail line asks for it): the BabbleSim crypto mode. Our runs use the default (plain text, no real AES); the stock script uses `-RealEncryption=1`. With the same stock binaries, plain-text mode works on nrf52_bsim (1c) and fails with reason 0x3d on nrf54lm20bsim (1d), which reproduces our symptom without any of our code. So the nRF54 BabbleSim model's plain-text mode fails MIC checks; real-AES mode works. Our own test A passes on nrf54lm20bsim once the flag is given (2a). The earlier note in docs/devices-control-notes.md section 6.1 item 1 ("the common part is the simulated nRF54 radio and encryption models") is right about plain-text mode, wrong that no pairing can complete on the chip.

Open and not tested: why the 54 plain-text mode fails (model bug or by design; I did not read NHW_54_AAR_CCM_ECB.c); tests B and C and the other boards (nrf54l15bsim) with the flag; whether the other helper's run.sh should pass the flag (the lead decides; I did not change control/). Run 2a is a diagnostic beyond the two registered tests, added after 1b to name the difference. Runs before the final ones: two failed attempts of 2a (20261111-212230-ctl-realenc-A.log: exit 1, the added LD_LIBRARY_PATH broke the container's python; 20261111-212252-ctl-realenc-A2.log: sed copy made without the library path, so the models could not load libCryptov1.so and ran plain text, RESULT FAIL A, same failure as before), kept in the log folder. Search runs find*.log only list SDK files.

## Cleanup

Removed from the server: /root/ring-os/ws/out/probe54 and /root/ring-os/src-probe54 (listing showing both gone: 20261111-212526-cleanup2.log). remote.sh's own run files for this probe stay in /root/ring-os/logs and /root/ring-os/runs (names ending -find*, -stock-conn-*, -plain-*, -ctl-realenc-*, -cleanup*); not removed.

RESULT: done, the stock encrypting pair reaches an encrypted link on nrf54lm20bsim so the hypothesis fails; the difference is BabbleSim's default plain-text mode (no -RealEncryption=1), which fails with 0x3d on the nRF54 model only, and our test A passes there once the flag is given.
