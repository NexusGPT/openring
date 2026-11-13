# os-infra notes: build and test workspace

Date: 2026-11-11, 10:24 to 11:55 CET. Helper: os-infra. No git was run.
Raw evidence for every line below is in `firmware/build-logs/infra/` (called `infra/` below) and in the run logs in `firmware/build-logs/`.

## Versions and tags

- Toolchain image: `ghcr.io/nrfconnect/sdk-nrf-toolchain:v3.4.2`, digest `sha256:54d1b800cc92602b5206b21a447696982177ac89cdef8c8ca8ef5cab419e0046` (`build-logs/20261111-103243-setup.log` line 10). Why this tag: sdk-nrf `.github/workflows/docker.yml` lines 58-62 tag the image with the git tag name (`infra/src-sdk-nrf-v3.4.2-docker.yml`); the registry answered 200 for `v3.4.2` (`infra/01-ghcr-manifest-v3.4.2.status`).
- In the image: west v1.5.0, host gcc 13.3.0, Ubuntu 24.04.5, and the 32-bit C library is already installed (gcc-multilib, libc6-dev-i386); `make` is missing (`infra/03b-image-tools.log`).
- Derived image `ring-os-toolchain:v3.4.2` (id 39c9d4914d92) from `firmware/tools/Dockerfile`: adds `make` and lists the 32-bit packages so a later base keeps them.
- Workspace: sdk-nrf v3.4.2 at f0b8ad4c, Zephyr 4.4.2 (ncs-v3.4.2, 9133dab6b066).

## Decisions

- `west.yml`: workspace application form, imports sdk-nrf v3.4.2; `group-filter: [+babblesim]` (sdk-nrf filters it out, `infra/src-sdk-nrf-v3.4.2-west.yml` line 48); `name-blocklist: [matter]` to narrow the update. `west update --narrow -o=--depth=1`; the workspace took 2.3 GB after the update (`build-logs/20261111-103243-setup.log` line 720).
- ring_core is added with `ZEPHYR_EXTRA_MODULES` in `app/CMakeLists.txt`, only when `modules/ring_core/zephyr/module.yml` exists. Why: ring_core lives in the manifest repository itself, which west does not list as a module, and the check lets the app build without it.
- Container layout: `/root/ring-os/ws` is mounted at `/ws`, the source copy at `/ws/firmware` (the manifest repository).
- The simulated chip target at v3.4.2 is `nrf54lm20bsim/nrf54lm20a/cpuapp`. The name in the brief and research-sdk.md, `nrf54lm20bsim/nrf54lm20/cpuapp`, is refused: "Board qualifiers `nrf54lm20/cpuapp` for board `nrf54lm20bsim` not found" (`build-logs/20261111-105344-build-all.log` lines 778-786).
- The 2 s simulated run uses the BabbleSim phy with `-sim_length=2e6`, because the board has no `-stop_at` option (`build-logs/20261111-105509-build-all.log` line 1002).
- Twister: one run on native_sim for every test, one run per bsim board for the tests that name it in `platform_allow` (`tools/bsim_tests.py` reads the yaml).

## Commands run (each from the project folder on the Mac)

| Run | Command | Exit | Log |
|---|---|---|---|
| setup | `sh firmware/tools/remote.sh -H setup "bash tools/setup_server.sh"` | 0 | `build-logs/20261111-103243-setup.log` |
| build_all, try 1 | `sh firmware/tools/remote.sh build-all "tools/build_all.sh"` | 126, script not executable | `build-logs/20261111-105254-build-all.log` |
| try 2 | same | 1, wrong bsim board name | `build-logs/20261111-105344-build-all.log` |
| try 3 | same | 1, `-stop_at` refused | `build-logs/20261111-105509-build-all.log` |
| try 4 | same | 0 | `build-logs/20261111-110009-build-all.log` |
| proof 1 | skeleton copy, `RING_REMOTE_SRC=/root/ring-os/src-skeleton` | 0 | `build-logs/20261111-110248-build-all-skeleton.log` |
| proof 4 | broken copy | 1 | `build-logs/20261111-110533-build-all-broken.log` |
| proof 2 | `sh firmware/tools/remote.sh kit-samples "tools/kit_samples.sh"` | 0 | `build-logs/20261111-110741-kit-samples.log` |
| proof 3 | `sh firmware/tools/remote.sh bsim-hr "tools/bsim_hr_demo.sh"` | 0 | `build-logs/20261111-111017-bsim-hr.log` |
| extra | failing-test copy | 1 | `build-logs/20261111-112002-build-all-failtest.log` |
| live tree | `sh firmware/tools/remote.sh build-all "tools/build_all.sh"` (ring_core present) | 0 | `build-logs/20261111-113215-build-all.log` |
| final | same, after adding the disk check to remote.sh | 0 | `build-logs/20261111-114413-build-all.log` |

## Proofs

1. Skeleton without ring_core: the copy had no `modules/ring_core` and no `tests/core` (`infra/30-skeleton-copy-files.txt`). Log says "ring_core module absent", dk build exit 0, bsim run prints `ring-os start: app 0.1.0-dev, zephyr 4.4.2, board nrf54lm20bsim/nrf54lm20a/cpuapp`, tests 1 of 1 passed on native_sim and on nrf54lm20bsim, last line `RESULT PASS`, remote exit 0. App on the kit: FLASH 34304 B, RAM 6024 B; MCUboot: FLASH 45656 B, RAM 21968 B.
2. Kit samples, all four builds exit 0, `RESULT PASS`:
   - peripheral_hids_keyboard, nrf54lm20dk: FLASH 214052 B (10.27%), RAM 37380 B (7.14%).
   - peripheral_hids_keyboard, nrf54lm20bsim/nrf54lm20a/cpuapp: builds.
   - peripheral_ancs_client, nrf54lm20dk: FLASH 170188 B (8.16%), RAM 33544 B (6.41%).
   - peripheral_ancs_client, nrf54lm20bsim/nrf54lm20a/cpuapp: builds.
   - The nrf54l15bsim fallback was not needed. The kit builds have one image each (no MCUboot in these samples' default).
3. Two devices: Zephyr peripheral_hr and central_hr on nrf54lm20bsim/nrf54lm20a/cpuapp, 10 simulated seconds; phy, peripheral and central exit 0; the central printed 9 lines `[NOTIFICATION] data ... length 2` (first at 1.047810 s). That text is printed only by central_hr's notify_func (`infra/60-central_hr-src-grep.log`).
4. Broken copy: a syntax line added to `app/src/main.c` (`infra/40-broken-diff.txt`). Result `RESULT FAIL dk-build bsim-build`, remote exit 1. The real `app/src/main.c` was never changed. Extra: a copy with a wrong assertion in `tests/smoke` gives `RESULT FAIL tests-native_sim tests-nrf54lm20bsim_nrf54lm20a_cpuapp`, exit 1 (`infra/42-failtest-diff.txt`).
5. Disk (`infra/70-proof5-disk.log`, `infra/71-proof5-du-each.log`, `infra/90-final-server-state.log`): `/root/ring-os` 3.4 GB at the end (workspace 3.1 GB of it, of which build outputs `ws/out` 795 MB and BabbleSim 42 MB, measured at 10:30 UTC). Images: 7.77 GB base and 7.96 GB derived as listed, sharing 6.063 GB, so about 9.7 GB on disk. Free on `/`: 72 GB at the start, 52 GB at the end (other people's jobs also write there).

## Final run (live tree, with the other helper's ring_core and tests/core)

`build-logs/20261111-114413-build-all.log`: free disk 52 GB, dk exit 0, bsim run start line found, native_sim 2 of 2 configurations passed (183 of 183 cases), nrf54lm20bsim 2 of 2 configurations passed (183 of 183 cases), `RESULT PASS`, exit 0. The case count grows as os-core adds tests (178 in the 11:32 run).

remote.sh now stops when less than 25 GB are free on the server's `/`. It got this check after proofs 1 to 4; those runs used the same script without it (free disk was checked by hand before the kit and two-device runs: `infra/50-df-before-kit.log`, `infra/60-central_hr-src-grep.log`).

## Notes and open points

- The server is shared and loaded; the failing-test run started at 11:20:02 CET (its id) and its first stage at 10:29:31 UTC (`infra/43-failtest-console.log`), about 9 minutes spent in the copy and the container start. remote.sh polls every 10 s and gives up only after 60 failed polls.
- Builds use `git describe` and print "not a git repository" because `.git` is not copied; the app version comes from `app/VERSION`.
- The bsim runs use the container's own `/tmp` for BabbleSim's pipes; it goes away with the container.
- The os-core helper already runs `tools/remote.sh` against the shared `/root/ring-os/src`; parallel runs can overwrite each other's copy there. Test copies should use `RING_REMOTE_SRC`.
- Not done: no ring board file; nothing on hardware; the ring_core module is compiled in but not called by `main.c`.

## State at the save point (2026-11-11, written after the final run)

- Done: every item of the brief; the final run is `build-logs/20261111-114413-build-all.log` (RESULT PASS, exit 0).
- Running on the server for os-infra: nothing. Every run started by os-infra has written its exit file in `/root/ring-os/logs/`.
- Next step: none for os-infra. The lead reruns `sh firmware/tools/remote.sh build-all "tools/build_all.sh"` and commits.

RESULT: done, one command builds the app for the kit and the simulated chip and runs all tests on the server with RESULT PASS, and the four proofs pass with logs.
