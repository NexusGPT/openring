# Research: nRF Connect SDK and Zephyr parts for a BLE ring (notifications, HID remote, no-hardware tests)

Read date: 2026-11-11 (UTC).
Pinned sources: nRF Connect SDK tag `v3.4.2` (github.com/nrfconnect/sdk-nrf). Its `west.yml` pins Zephyr `ncs-v3.4.2` (github.com/nrfconnect/sdk-zephyr, file `west.yml` line 66-68) and nrfxlib `v3.4.2`. `v3.4.2` is the newest stable tag found with `git ls-remote --tags`. A `v3.5.0-preview4` tag exists but was not read.

Tags: [F] = file text read (raw.githubusercontent.com, piped to grep/sed; line numbers from those commands). [S] = directory listing from the GitHub git-tree API (names only), or a WebFetch summary (not verbatim).

Copies: saved copies are in the scratchpad folder `<scratch>/`. This file is the only file written in the design folder, as the brief requires.

Base URL for sdk-nrf: `https://raw.githubusercontent.com/nrfconnect/sdk-nrf/v3.4.2/`
Base URL for sdk-zephyr: `https://raw.githubusercontent.com/nrfconnect/sdk-zephyr/ncs-v3.4.2/`

## 1. Apple Notification Center Service (ANCS) client

- Library header: `include/bluetooth/services/ancs_client.h` [S, path exists]. Public functions with line numbers [F]: `bt_ancs_client_init` (line 434), `bt_ancs_subscribe_notification_source` (445), `bt_ancs_subscribe_data_source` (456), `bt_ancs_unsubscribe_notification_source` (466), `bt_ancs_unsubscribe_data_source` (475), `bt_ancs_register_attr` (488), `bt_ancs_register_app_attr` (503), `bt_ancs_request_attrs` (517), `bt_ancs_request_app_attr` (531), `bt_ancs_notification_action` (545), `bt_ancs_handles_assign` (562, takes `struct bt_gatt_dm *dm`).
- Kconfig: `subsys/bluetooth/services/Kconfig.ancs_client` [F]. Line 7: `menuconfig BT_ANCS_CLIENT`. Line 8: `bool "Apple Notification Center Service client"`. Line 9: `select BT_NRF_SERVICES`. Line 15-17: `config BT_ANCS_CLIENT_CP_BUFF_SIZE`, `default 160`, range 20 to 65535. Only this one option is in the file.
- Library doc: `doc/nrf/libraries/bluetooth/services/ancs_client.rst` [F]. Line 21: "The NP is typically an iOS device that is acting as a server." Line 24: "In this library, iOS notifications are received through the GATT notifications." Line 40-41: "Once a connection is established with a central device, the library needs a service discovery to discover the ANCS server handles." and "If this succeeds, the handles for the ANCS server must be assigned to an ANCS client instance using the :c:func:`bt_ancs_handles_assign` function." Line 15: "Apple can change the server implementations such as the ones found in iOS at any time, which may cause this client implementation to stop working." Line 91: "There are no dependencies for using this library." The doc does not state a bonding rule.
- Sample: `samples/bluetooth/peripheral_ancs_client` [F].
  - `sample.yaml` line 8-11 (integration_platforms): nrf52840dk/nrf52840, nrf5340dk/nrf5340/cpuapp, nrf54h20dk/nrf54h20/cpuapp. Line 17: "      - nrf54lm20dk/nrf54lm20a/cpuapp" (in `platform_allow`, not in integration_platforms).
  - `README.rst` line 17: "The sample also requires a device running an ANCS Server to connect with (for example, an iPhone which runs iOS, or a Bluetooth® Low Energy dongle and the `Bluetooth Low Energy app`_)."
  - `README.rst` line 88: "Observe that notifications that are displayed in the iOS notification tab also show up on the UART from the sample."
  - `src/main.c` line 47: `BT_DATA_BYTES(BT_DATA_SOLICIT128, BT_UUID_ANCS_VAL),` (service solicitation in advertising).
  - `src/main.c` line 149 `discover_ancs_completed_cb`, line 159 `err = bt_ancs_handles_assign(dm, ancs_c);`, line 308 `bt_gatt_dm_start(conn, BT_UUID_ANCS, ...)`.
  - `src/main.c` line 357: `sec_err = bt_conn_set_security(conn, BT_SECURITY_L2);`.
  - `prj.conf` line 13 `CONFIG_BT_SMP=y`, line 15 `CONFIG_BT_GATT_DM=y`, line 18 `CONFIG_BT_ANCS_CLIENT=y`, line 21 `CONFIG_BT_GATTP=y`, line 23 comment `# Enable bonding`, line 24 `CONFIG_BT_SETTINGS=y`.
  - `README.rst` line 120: "Check :guilabel:`Perform Bonding` and :guilabel:`Enable LE Secure Connection pairing`" (test with the BLE app).
- Requirements in one line: the sample needs SMP, GATT client and DM, encryption at security level 2, and settings for bonds. These are sample settings, not library rules.

## 2. Apple Media Service (AMS) client and Current Time Service (CTS) client

AMS:
- Header `include/bluetooth/services/ams_client.h` [S, path exists]. Source `subsys/bluetooth/services/ams_client.c` (named in `doc/nrf/libraries/bluetooth/services/ams_client.rst` line 21) [F].
- Doc line 11-12: "You can use this library as a Media Remote (MR) to interact with a Media Source (MS). The MS is typically an iOS device." Line 15: "The AMS Client is used in the :ref:`peripheral_ams_client` sample." [F]
- Kconfig: `Kconfig.ams_client` exists in `subsys/bluetooth/services` [S]. Not read.
- Sample `samples/bluetooth/peripheral_ams_client` [F]:
  - `sample.yaml` line 8-11: integration_platforms are nrf52840dk, nrf5340dk cpuapp, nrf54h20dk cpuapp. Line 17: "      - nrf54lm20dk/nrf54lm20a/cpuapp" (platform_allow).
  - `prj.conf` line 14 `CONFIG_BT_GATT_CLIENT=y`, line 15 `CONFIG_BT_GATT_DM=y`, line 18 `CONFIG_BT_AMS_CLIENT=y`, line 21 `CONFIG_BT_SETTINGS=y`.
  - `src/main.c` line 41: `BT_DATA_BYTES(BT_DATA_SOLICIT128, BT_UUID_AMS_VAL),`. Line 198 `bt_ams_subscribe_remote_command(ams_c, notify_rc_cb)`, line 204 `bt_ams_subscribe_entity_update(...)`. Line 293 `sec_err = bt_conn_set_security(conn, BT_SECURITY_L2);`. Line 322 `bt_gatt_dm_start(conn, BT_UUID_AMS, &discover_cb, &ams_c);`.

CTS:
- Header `include/bluetooth/services/cts_client.h` [S]. Source `subsys/bluetooth/services/cts_client.c` (doc line 18) [F].
- Doc `doc/nrf/libraries/bluetooth/services/cts_client.rst` line 10: "You can use the CTS Client library to retrieve the current time from a connected peer that is running the GATT server with the `Current Time Service`." Line 12: "The CTS Client is used in the :ref:`peripheral_cts_client` sample." [F]
- Kconfig: `Kconfig.cts_client` exists [S]. Not read.
- Sample `samples/bluetooth/peripheral_cts_client` [F]:
  - `sample.yaml` line 7-8: integration_platforms `nrf54l15dk/nrf54l15/cpuapp`. Line 19: "      - nrf54lm20dk/nrf54lm20a/cpuapp" (platform_allow).
  - `prj.conf` line 18 `CONFIG_BT_CTS_CLIENT=y`, line 15 `CONFIG_BT_GATT_DM=y`.
  - `src/main.c` line 41: `BT_DATA_BYTES(BT_DATA_SOLICIT16, BT_UUID_16_ENCODE(BT_UUID_CTS_VAL)),`. Line 130-131: `if (bt_conn_get_security(cts_c.conn) < BT_SECURITY_L2) { err = bt_conn_set_security(cts_c.conn, BT_SECURITY_L2);`. Line 199 `bt_gatt_dm_start(conn, BT_UUID_CTS, &discover_cb, NULL);`.
- Requirements: service solicitation (advertising data), GATT DM, and security level 2 before subscribing (line 106).
- Bonding: `sample.yaml` says the test is "Starting Current Time Service client sample" and "Advertising successfully started" (lines 37-38). No bonding rule is stated in the doc read.

## 3. HID over GATT (HIDS) and HID samples

- HIDS library doc `doc/nrf/libraries/bluetooth/services/hids.rst` [F]. Line 22-23: "Some systems require security to use the HID Service. To ensure interoperability, enable the :kconfig:option:`CONFIG_BT_HIDS_DEFAULT_PERM_RW_ENCRYPT` Kconfig option." Line 28: ":ref:`peripheral_hids_keyboard`" (listed sample).
- Header `include/bluetooth/services/hids.h` [F, path exists]. `bt_hids_init` at line 601. `bt_hids_inp_rep_send_userdata` at line 653. `static inline int bt_hids_inp_rep_send` at line 672.
- Keyboard sample `samples/bluetooth/peripheral_hids_keyboard` [F]:
  - `sample.yaml` lines 21-29 integration_platforms: nrf52dk/nrf52832, nrf5340dk cpuapp/ns, nrf54h20dk, nrf54l15dk/nrf54l05, nrf54lm20dk/nrf54lm20a/cpuapp (line 26), nrf54lm20dk/nrf54lm20b/cpuapp (line 27), nrf54ls05dk, nrf54lc10dk.
  - `README.rst` line 33: "It uses a report map for a generic keyboard."
  - `src/main.c` line 655 `static const uint8_t report_map[] = {` to line 702 `0xC0 /* End Collection (Application) */`. The keyboard report map has no Consumer page (0x0C). A search for `consumer` or `0x0c` in `src/main.c` returned only line 702 (`0xC0`).
- Mouse sample `samples/bluetooth/peripheral_hids_mouse` [F]:
  - `sample.yaml` line 27 lists `nrf54lm20dk/nrf54lm20a/cpuapp` in integration_platforms.
  - `src/main.c` line 721 `static const uint8_t report_map[] = {`, line 771 `0x05, 0x0C, /* Usage Page (Consumer) */`, line 772 `0x09, 0x01, /* Usage (Consumer Control) */`, closing `};` at line 798. So a consumer-control collection is written into the mouse sample's report map (as raw bytes, not a helper).
- nRF Desktop consumer report macro: `applications/nrf_desktop/configuration/common/hid_report_consumer_ctrl.h` [F]. Line 21 `#define REPORT_MAP_CONSUMER_CTRL(report_id)`, line 27 `0x2A, 0xFF, 0x03, /* Usage maximum (0x3FF) */`.
- Board lists: keyboard and mouse both list nrf54lm20a (see above). Keyboard `sample.yaml` line 38 and mouse line 39 list `nrf54lm20dk/nrf54lm20a/cpuapp` in platform_allow.
- Notes: the nRF Desktop report macro is a helper in an application (not a library). Consumer control in the SDK is therefore a report map written by hand.

## 4. nRF54LM20A support in the controller and board lists

- Board definition in Zephyr: `boards/nordic/nrf54lm20dk/` in sdk-zephyr `ncs-v3.4.2` [S, file listing]. Files include `nrf54lm20dk_nrf54lm20a_cpuapp.yaml`, `nrf54lm20dk_nrf54lm20a_cpuapp_ns.yaml`, and `nrf54lm20dk_nrf54lm20b_cpuapp.yaml`. Not read as text.
- Simulated board: `boards/native/nrf_bsim/doc/nrf54lm20bsim.rst` [F]. Line 15-16: "To allow simulating nRF54LM20 SOCs, a Zephyr target board is provided: the ``nrf54lm20bsim/nrf54lm20/cpuapp``." Line 49: "* RADIO".
- Controller (SoftDevice Controller, nrfxlib tag `v3.4.2`) [F]: `softdevice_controller/README.rst` line 10: "The libraries are available as soft-float, softfp-float, and hard-float builds for the nRF52, nRF54H and nRF54L Series, and as a soft-float build for the nRF53 Series." The file names the nRF54L Series, not nRF54LM20 by name. Line 88: "For the nRF54L Series devices, the SoftDevice Controller in non-secure mode is experimental."
- sdk-nrf samples that list an nrf54lm20 target, read in `sample.yaml` [F] at v3.4.2:
  - `peripheral_ancs_client` (platform_allow line 17)
  - `peripheral_ams_client` (platform_allow line 17)
  - `peripheral_cts_client` (platform_allow line 19)
  - `peripheral_hids_keyboard` (integration line 26, platform_allow line 38)
  - `peripheral_hids_mouse` (integration line 27)
  - `peripheral_with_multiple_identities` (platform_allow line 19)
- Other samples with nrf54lm20 paths exist, for example `central_hids/boards/nrf54lm20dk_nrf54lm20a_cpuapp.conf` [S]. Their `sample.yaml` files were not read.
- Not found: a code search for `nrf54lm20` in sample.yaml files. The GitHub code search API returned `401 Requires authentication` (not worked around).
- nRF Desktop has a configuration folder `applications/nrf_desktop/configuration/nrf54lm20dk_nrf54lm20a_cpuapp/` [S, listing].

## 5. More than one connection as a peripheral

- Zephyr Kconfig, sdk-zephyr `ncs-v3.4.2` [F]:
  - `CONFIG_BT_MAX_CONN`: `subsys/bluetooth/Kconfig` line 102-109. Line 109: "Maximum number of simultaneous Bluetooth connections". Range 1 to 250, default 1.
  - `CONFIG_BT_MAX_PAIRED`: `subsys/bluetooth/host/Kconfig` line 886. Line 892-893: "Maximum number of paired Bluetooth devices. The minimum (and default) number is 1." Range 0 to 250.
  - `CONFIG_BT_ID_MAX`: `subsys/bluetooth/host/Kconfig` line 1023. Line 1029-1030: "Maximum number of supported local identity addresses. For most products this is safe to leave as the default value (1)." Range 1 to 250, default 1.
  - `CONFIG_BT_EXT_ADV_MAX_ADV_SET`: `subsys/bluetooth/Kconfig.adv` line 30. Line 35-36: "Maximum number of simultaneous Bluetooth advertising sets" and "supported." Range 1 to 64, default 1. (Not in `host/Kconfig`.)
- nRF Desktop bond module `applications/nrf_desktop/doc/ble_bond.rst` [F]:
  - Line 13: "* Switching between peers (only for nRF Desktop peripheral)."
  - Line 48: "  * nRF Desktop peripheral uses multiple local identities."
  - Line 54: "Only one Bluetooth peer can be bonded with a given local identity."
  - Line 57-58: "When the device changes the selected Bluetooth peer, it actually switches its own local identity. The old peer is disconnected by the application, Bluetooth advertising is started, and the new peer connects."
  - Line 120-124: erase advertising keeps the old peer until the new one bonds.
- Sample `samples/bluetooth/peripheral_with_multiple_identities` [F]:
  - `prj.conf` line 14 `CONFIG_BT_EXT_ADV_MAX_ADV_SET=20`, line 15 `CONFIG_BT_MAX_CONN=20`, line 16 `CONFIG_BT_ID_MAX=20`.
  - `README.rst` line 6: "The sample demonstrates how to use a single physical device to create and manage multiple advertisers, making it appear as multiple distinct devices by assigning each a unique identity."
  - `README.rst` line 7: "You can use this sample to test a central device that requires connections to multiple peripheral devices when you do not have several development kits available."
- Not found: a sample in which one peripheral holds two central connections at the same time. The sample list was checked by name only. `central_and_peripheral_hrs` exists [S] and was not read.

## 6. Testing with no hardware

(a) native_sim host support [F unless marked]:
- `boards/native/native_sim/doc/index.rst` line 6-8: "The ``native_sim`` board is a :ref:`POSIX architecture<Posix arch>` based board. With it, a Zephyr application can be compiled together with the Zephyr kernel, and libraries, creating a normal Linux executable."
- Line 376: "Note that this device can only be used with Linux hosts." (the zeth TAP network driver).
- Line 396-403 (host Bluetooth adapter): "It's possible to use the host's Bluetooth adapter as a Bluetooth controller for Zephyr." and line 399-401 "sudo zephyr.exe --bt-dev=hci0. Using the device requires root privileges". Line 405-406: HCI TCP "virtual Bluetooth controller over TCP".
- Line 421-430 (display): "**Display driver** A display driver is provided that creates a window on the host machine to render display content." (line 424-425). Line 428-430: needs the SDL2 development library on the host; "For 64bit native_sim builds you need to have the 64bit version installed."
- macOS and 32-bit (WebFetch summary [S], `https://docs.zephyrproject.org/latest/boards/native/doc/arch_soc.html`, section "Overview > Host system dependencies"): "This port is designed and tested to run in Linux." "The POSIX architecture is known to not work on macOS due to fundamental differences between macOS and other typical Unixes." "To build for the 32bit targets you must have the 32-bit C library installed in your system" (gcc-multilib on Debian/Ubuntu). This is a summary, not verbatim text.

(b) BabbleSim boards [F]:
- `boards/native/nrf_bsim/doc/nrf52_bsim.rst` line 18-19: "This uses `BabbleSim`_ to simulate the radio activity, and the :ref:`POSIX architecture<Posix arch>` and the `native simulator`_ to run applications natively on the development system." Line 26: "* Radio". Line 62-63: "This board requires the host 32 bit C library."
- Line 71-74: `west config manifest.group-filter -- +babblesim`, `west update`, `make everything -j 8`. Line 84-85: `BSIM_OUT_PATH` and `BSIM_COMPONENTS_PATH`.
- Line 158-161 (two devices, from the doc): `./bs_nrf52_bsim_samples_bluetooth_peripheral_hr -s=trial_sim -d=0 &`, `./bs_nrf52_bsim_samples_bluetooth_central_hr -s=trial_sim -d=1 &`, `./bs_2G4_phy_v1 -s=trial_sim -D=2 -sim_length=10e6 &`. Line 163-167: "-s" names the simulation, "-D" is the device count, "-d" the device number.
- `boards/native/nrf_bsim/doc/nrf54l15bsim.rst`: line 15-16 "nrf54l15bsim/nrf54l15/cpuapp". Line 30-32: "Unlike real nRF54L15 devices, the nrf54l15bsim target has unlimited RAM". Line 36: "This simulated target does **not** yet support targeting the cpuflpr core." Line 43 CRACEN, line 51 RADIO.
- `boards/native/nrf_bsim/doc/nrf54lm20bsim.rst`: line 15-16, 24-25, 34 (no cpuflpr), 49 RADIO.
- nrf5340bsim: `boards/native/nrf_bsim/doc/nrf5340bsim.rst` [S] (listed, not read).
- `doc/develop/test/bsim.rst` line 9-10: "we use the `Babblesim`_ simulator to test some of the Zephyr radio protocols, including the Bluetooth LE stack". Line 35-38: "tests without radio activity ... can be used just like native_sim with twister". Line 43-45: "tests with radio activity ... are not build and run with twister, but with a dedicated set of tests scripts." Line 47: "The ``compile.sh`` and ``run_parallel.sh`` scripts contained in that folder are used by the CI system". Line 97: `${ZEPHYR_BASE}/tests/bsim/compile.sh`. Line 102: `${ZEPHYR_BASE}/tests/bsim/run_parallel.sh`.
- Running two BLE devices is in the nrf52_bsim doc (lines 149-167 above).

(c) sdk-nrf building its own samples for a bsim board: not checked in the sample.yaml content. The sdk-nrf tree has `tests/bluetooth/bsim` [S] (path listing only). Not found: a sample.yaml in sdk-nrf that lists a bsim board.

(d) Twister and ztest:
- `doc/develop/test/twister.rst` line 63: `$ ./scripts/twister --all --enable-slow`. Line 75-78: "--platform" filter and "--platform board@revision". Line 86 `scripts/twister --help`.
- `doc/develop/test/ztest.rst` line 16: "Using Ztest to create a test suite is as easy as calling the :c:macro:`ZTEST_SUITE`." Line 135: `ZTEST(my_suite, test_fail)`. Line 240: "``your.test.scenario.name`` references a test scenario defined in :file:`testcase.yaml`".
- Not found: a `west twister` command line in `twister.rst` (grep returned no hit).

## 7. Display side: LVGL and native_sim display

- LVGL demos sample `samples/modules/lvgl/demos/sample.yaml` [F]: line 2 "LVGL sample, containing all upstream demos". Line 5-6 `modules:` `- lvgl`. Line 8 `filter: dt_chosen_enabled("zephyr,display")`. The platform list lines 10-14 has NXP boards only.
- native_sim devicetree `boards/native/native_sim/native_sim.dts` [F]: line 24 `zephyr,display = &sdl_dc;`, line 197-198 `sdl_dc: sdl_dc {` with `compatible = "zephyr,sdl-dc";`.
- SDL display driver config `drivers/display/Kconfig.sdl` [F]: line 7 `menuconfig SDL_DISPLAY`, line 13 "Enable SDL based emulated display compliant with display driver API."
- Inference (not tested): because native_sim sets `zephyr,display`, the LVGL demos filter would accept it. Not verified by a build.
- LVGL module docs and the LVGL module's own sample list beyond the demos were not read.

## 8. Size and memory

- Not found: flash or RAM figures for HIDS, ANCS client, or LVGL. Read: `doc/nrf/libraries/bluetooth/services/hids.rst` and `ancs_client.rst` [F] (grep for footprint, flash, RAM, kB, bytes, memory gave no figures).
- Not found: `rom_report` or `ram_report` text in `doc/develop/optimizations/footprint.rst` [F] (grep showed only stack size lines 6-26). Zephyr has `scripts/footprint/` and `.github/workflows/footprint-tracking.yml` [S, listing only].

## 9. Building on a development computer

- Stable `west init` line: `doc/nrf/installation/install_ncs.rst` line 280: "west init -m https\://github.com/nrfconnect/sdk-nrf --mr *nRFConnectSDK_revision* *nRFConnectSDK_revision_workspace_dir*". Line 629: "Alternatively, you can omit the ``--mr`` parameter, in which case west uses ``main`` as the default". [F]
- Zephyr SDK installer `doc/develop/toolchains/zephyr_sdk.rst` (`ncs-v3.4.2`) [F]: line 33 "The Zephyr SDK bundle supports all major operating systems (Linux, macOS and" (the line continues in the source). Line 143 `./setup.sh` (Linux group). macOS group tab at line 159. Line 168 `curl -L -O |sdk-url-macos|`.
- Zephyr getting-started `doc/develop/getting_started/index.rst` [F]: line 430-435 and 445-450 use `west sdk install`.
- Docker, Nordic: `scripts/docker/README.rst` [F] line 10: "The image is based on the official Docker image for Ubuntu Linux 24.04". Line 55: `docker run -ti -v /dev:/dev -v /run/udev:/run/udev:ro --privileged -e ACCEPT_JLINK_LICENSE=1 ghcr.io/nrfconnect/sdk-nrf-toolchain:<TAG> bash`. Image name from `.github/workflows/docker.yml` [F] line 16: `IMAGE_NAME: ghcr.io/${{ github.repository }}-toolchain`.
- Docker, Zephyr: not found in the Zephyr getting-started or docs read. Only a CI image is seen: `.github/workflows/bsim-tests.yaml` [F] line 44-45 `container: image: ghcr.io/zephyrproject-rtos/ci-repo-cache:v0.29.1.20260327`. This is a CI cache image, not documented for developers.
- GitHub Actions examples [F]: `.github/workflows/bsim-tests.yaml` line 40 `bsim-test:`, line 49-50 `BSIM_OUT_PATH: /opt/bsim/`, `BSIM_COMPONENTS_PATH: /opt/bsim/components`. `.github/workflows/twister.yaml` line 28 `runs-on: ubuntu-24.04`, line 129 `container:`.

## Not found (summary)

- Kconfig for AMS and CTS clients: not read (paths only).
- A peripheral holding two central connections at once: not found in the sample names checked.
- nrf54lm20 named in SoftDevice Controller docs: not found (the doc says nRF54L Series).
- sdk-nrf bsim sample listing: not checked.
- Figures for HIDS, ANCS, LVGL memory: not found.
- Zephyr developer Docker image: not found.

RESULT: done, all nine questions have findings or "not found" with the paths tried, with the macOS host limit from a WebFetch summary (not verbatim).
