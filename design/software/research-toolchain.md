# Research: nRF54LM20A toolchain, nPM1304 and bring-up (Nordic documentation first)

Date read: 2026-11-11 (UTC 07:49 to 07:58).
Tags: [F] = page opened and read. [S] = search snippet only, page not read.
Saved copies: `<scratch>/toolchain-evidence/`
(short names below refer to files in that folder).
Method note: `curl` saved the Zephyr pages and the Zephyr GitHub files as raw copies (line numbers are in those copies). WebFetch returns a summary by a small model, so quotes marked "WebFetch" must be checked on the page before they go into a document.

Key points first:
- Nordic says there is no development kit for the nRF54LM20A. Zephyr's `nrf54lm20dk/nrf54lm20a/...` target is an emulation on the nRF54LM20 DK (PCA10184).
- The nRF54LM20A DK support was "experimental" in SDK v3.1.1 (WebFetch of the release notes).
- Nordic's install page (WebFetch) lists macOS 26 as "Not supported." The layout is unclear. Check it before you install on macOS.
- Debug out voltage limits for the nRF54LM20 DK were not found in a readable source.
- No nPM1304 fuel-gauge driver or binding found in Zephyr. The charger has a Zephyr binding and driver.

## 1. SDK version, board target, nPM1304 drivers and bindings

- Board target: `nrf54lm20dk/nrf54lm20a/cpuapp`. [F] https://docs.zephyrproject.org/latest/boards/nordic/nrf54lm20dk/doc/index.html line 742: "nrf54lm20dk/nrf54lm20a/cpuapp target". Read by curl 2026-11-11. Saved copy: zephyr_dk_board_page.html, text in zephyr_dk_board_text.txt:742. Other targets on the same page: `nrf54lm20dk/nrf54lm20a/cpuapp/ns` (line 1029), `nrf54lm20dk/nrf54lm20a/cpuflpr` (line 1315), and the nRF54LM20B variants (line 2438, JSON list).
- Emulation, not a real A-variant kit. [F] same page, line 475: "nRF54LM20A emulation on nRF54LM20 DK". Lines 2532-2536: "The nrf54lm20dk/nrf54lm20a board is a modified version of the nRF54LM20 DK that enforces the limitations imposed by the nRF54LM20A IC, which is the NPU-less variant of the original nRF54LM20B IC. Since Nordic does not offer a development kit for the nRF54LM20A, you can use this board to develop for this IC while using the nRF54LM20 Development Kit (PCA10184)."
- First SDK version with support: [F] WebFetch of https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/releases_and_maturity/releases/release-notes-3.1.1.html (read 2026-11-11, summary of the page, offset 100000):
  - "This is the first release of the nRF Connect SDK that brings comprehensive experimental support for the nRF54LM20 DK..." (continues "and nRF54LM20A SoC.")
  - "This release provides experimental support for the nRF54LM20A SoC with the following features:"
  - "The nRF54LM20 DK board support is experimental."
  - No nRF54LM20 item is labelled full support on that page (WebFetch).
- Support matrix from v3.3.0 (conflicting or unread): [S] search snippet says a compatibility matrix shows nRF54LM20A from v3.3.0. The v3.3.0 release notes URL returned HTTP 404 (https://nrfconnectdocs.nordicsemi.com/ncs/v3.3.0/nrf/releases_and_maturity/releases/release-notes-3.3.0.html, [F] 404 via WebFetch). The matrix page was not read. So "full support from v3.3.0" is untested.
- Version labels on pages read (moving "latest" docs): install page says "the latest stable nRF Connect SDK release (v3.4.2)" [F WebFetch]. Zephyr DK page read via WebFetch says "SDK version: 4.4.99" [F WebFetch, unverified]. The AP-Protect page title says "nRF Connect SDK 3.4.99 documentation" [F WebFetch]. Pin a version in any document.
- nPM1304 in Zephyr:
  - MFD binding `nordic,npm1304`. [F] https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/dts/bindings/mfd/nordic,npm1304.yaml line 6: `compatible: "nordic,npm1304"`; line 8: `include: nordic,npm13xx-common.yaml`. Saved: zephyr_npm1304.yaml.
  - Regulator binding `nordic,npm1304-regulator`. [F] raw dts/bindings/regulator/nordic,npm1304-regulator.yaml line 11: `compatible: "nordic,npm1304-regulator"`; line 13: `include: "nordic,npm13xx-regulator-common.yaml"`. Saved: zephyr_npm1304-regulator.yaml. Also listed in https://github.com/zephyrproject-rtos/zephyr/tree/main/dts/bindings/regulator (saved zephyr_tree_regulator.html).
  - MFD driver: `drivers/mfd/mfd_npm13xx.c` listed in https://github.com/zephyrproject-rtos/zephyr/tree/main/drivers/mfd (saved zephyr_tree_src_drivers_mfd.html).
  - Charger binding `nordic,npm1304-charger`. [F] https://docs.zephyrproject.org/latest/build/dts/api/bindings/sensor/nordic,npm1304-charger.html, line 437: "drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c" (saved zephyr_npm1304_charger_binding.html, text zephyr_npm1304_charger_text.txt). Note: the GitHub `drivers/charger` listing has only npm10xx files (0 "npm13" hits, saved zephyr_tree_src_drivers_charger.html). So the charger driver sits under sensor, not charger.
  - Fuel gauge: not found. Zephyr GitHub listings `dts/bindings/fuel-gauge` (zephyr_tree_fuel-gauge.html) and `drivers/fuel_gauge` (zephyr_tree_src_drivers_fuel_gauge.html) show 0 "npm13" hits. Nordic has a sample `npm13xx_fuel_gauge` [S] (https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/samples/pmic/native/npm13xx_fuel_gauge/README.html), not read.
  - Nordic: [F] WebFetch of https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/app_dev/device_guides/pmic/npm1304.html: "There is no firmware for nPM1304 that can be built and programmed onto the PMIC."

## 2. Tool install on macOS, Windows, Linux

- Nordic, sdk-manager (the current route). [F] WebFetch of https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/installation/install_ncs.html, read 2026-11-11, body from offset 100000:
  - `nrfutil install sdk-manager`
  - `nrfutil sdk-manager search`
  - `nrfutil sdk-manager install <version>`
  - `nrfutil sdk-manager toolchain launch --ncs-version <version> \--shell` (Linux/macOS); `... \--terminal` (Windows)
  - Default paths: "The `sdk-manager` command installs the SDK by default at `C:/ncs/` on Windows" and "On macOS, the command defaults to `/opt/nordic/ncs/` and `/opt/nordic/ncs/toolchains`."
- VS Code: "Install SDK in VS Code" button "installs the latest version of nRF Connect for VS Code and the latest stable nRF Connect SDK release (v3.4.2)." [F WebFetch, same URL.]
- west and the SDK workspace: `pip3 install -U west` (Linux/macOS), `pip3 install --user -U west`, `west init -m https://github.com/nrfconnect/sdk-nrf --mr nRFConnectSDK_revision nRFConnectSDK_revision_workspace_dir`, `west update`, `west zephyr-export`. Environment: `source zephyr/zephyr-env.sh` (Linux/macOS), `zephyr\zephyr-env.cmd` (Windows). [F WebFetch, same URL.]
- OS support on the install page (WebFetch summary):
  - Windows 11 (x64): "Built and tested with Twister." ARM64: "Not supported."
  - Linux Ubuntu 24.04 LTS: "Built and tested with Twister. Comprehensive testing with Nordic Semiconductor hardware."
  - macOS 26: "Not supported." together with "Built and tested with Twister." The summary says the layout does not map each to x64 or ARM64. This host runs Darwin 25.6, which is macOS 26. Check the page or the release notes before you rely on macOS.
- Zephyr getting started (Zephyr, not Nordic) [F curl]: `brew install cmake ninja gperf python3 python-tk ccache qemu dtc libmagic wget openocd` (zephyr_gs_text.txt:553); `winget install Kitware.CMake Ninja-build.Ninja oss-winget.gperf Python.Python.3.12 Git.Git oss-winget.dtc wget 7zip.7zip` (line 592); `west init -m https://github.com/zephyrproject-rtos/zephyr zephyrproject` (line 695). Source: https://docs.zephyrproject.org/latest/develop/getting_started/index.html.
- nRF Connect for Desktop, Toolchain Manager, the nrfutil device commands: not found in readable pages. The nrfutil docs page (https://docs.nordicsemi.com/bundle/nrfutil/page/nrfutil.html) returned a bot-check page to curl. The WebFetch redirect target returned 404. Unverified.

## 3. Custom board: files, devicetree, Kconfig, hardware model v2

- Zephyr board porting [F] https://docs.zephyrproject.org/latest/hardware/porting/board_porting.html (curl, saved zephyr_board_porting.html, text zephyr_board_porting_text.txt):
  - line 502-507: "The transition from the previous hardware model to the current one (commonly referred to as “hardware model v2”) requires modifications to all existing board"
  - line 760: "board.yml: a YAML file describing the high-level meta data of the"
  - line 780: "board.cmake: used for Flash and debug support"
  - line 1163: "Look for board.cmake files for other boards similar to your own for"
  - line 1309-1315: "The board hardware model in Zephyr allows you to extend an existing board with new board variants... To extend an existing board, first create a board.yml in your extended"
  - Start from the DK's files: line 1163 (copy similar boards) and line 1315 (extend an existing board). The Zephyr page does not name the nRF54LM20 DK as the base.
- Nordic side [S] (search snippets, not read): board.yml is required per board folder in HWMv2; HWMv1 was removed in NCS v3.0.0; "Board names must be unique. Run `west boards`." Nordic Board Porting Guide: https://nrfconnectdocs.nordicsemi.com/ncs/latest/zephyr/hardware/porting/board_porting.html (not read).
- Known pitfall [S]: a DevZone thread "Custom board derived from nrf54l15dk failing to build" (https://devzone.nordicsemi.com/f/nordic-q-a/120979/custom-board-derived-from-nrf54l15dk-failing-to-build), not read.
- Not found: a readable Nordic page for the custom board file layout and Kconfig choice on nRF54L. Unverified.

## 4. Build, flash, recover, debug probe, voltage

- Build and flash on the DK [F] zephyr_dk_board_text.txt:2514-2522: "Follow the instructions in the Nordic nRF5x Segger J-Link page to install and configure all the necessary software." Commands: `west build -b nrf54lm20dk/nrf54lm20b/cpuapp samples/hello_world` then `west flash`. Note: this example uses the nrf54lm20b target, not nrf54lm20a.
- Flash tools table [F] zephyr_dk_board_text.txt:2455-2472: columns flash, debug, reset, rtt, debugserver, attach. Row `jlink`: flash ✅, debug ✅ (default), reset, rtt, debugserver, attach ✅. Row `nrfutil`: flash ✅ (default). Column mapping is inferred from the layout of the saved text.
- Readback protection [F] line 2506: `west flash --recover`. Line 2509: "The --recover command erases the flash memory and then writes a small binary into". Line 2511: "This binary prevents the readback protection from enabling itself again after a pin reset or power cycle." Zephyr sysbuild with MCUboot [F] https://docs.zephyrproject.org/latest/build/sysbuild/index.html, line 611: `west build -b reel_board --sysbuild samples/hello_world -- -DSB_CONFIG_BOOTLOADER_MCUBOOT=y ...` (example board reel_board, not the nRF54LM20; saved zephyr_sysbuild_text.txt).
- `nrfutil device program` / `recover` / `erase` syntax: not found in readable pages (see section 2).
- Debug probe: J-Link is the default debug probe in the Zephyr DK table (line 2464-2470). The external-target debug out details are not found in a readable source. Search snippet [S] (not read): the nRF54LM20 DK hardware guide lists a "Debug out header" and nRF:VDD 1.8 V to 3.3 V. The guide PDF (https://www.mouser.com/datasheet/3/926/1/nRF54LM20_DK_HW_User_Guide_v0.3.4.pdf) timed out in WebFetch. curl saved an HTML page, not the PDF (nrf54lm20_dk_hw_user_guide_v0.3.4.pdf). Not readable.
- Voltage limit for the nRF54L series: [S] search snippets say the nRF54LM20A datasheet lists supply 1.7 V to 3.6 V (https://docs.nordicsemi.com/r/09E6cV_58cJ3mJAVA8IpZA/Su~xnKbPwkpHYsW0r4jMEA, index page only read). A Mouser page gives 1.7 V to 3.5 V (conflict, unverified). The DK guide [S] has an external supply header at 1.7 V to 3.6 V. Confirm in the datasheet electrical section.
- External target debug out voltage (VTref) behaviour on the LM20 DK: not found. A DevZone thread on the nRF5340 DK says the probe drives SWD to the DK's VDD level (https://devzone.nordicsemi.com/f/nordic-q-a/127677/how-to-fix-the-voltage-mismatch-between-vtref-and-vdd-on-the-target-board/568434). That is a different kit. Unverified for LM20.

## 5. Logs without a UART: RTT, logging backends

- Zephyr logging [F] https://docs.zephyrproject.org/latest/services/logging/index.html (curl):
  - line 545: "destination, for example UART, RTT or BLE."
  - line 1293: "CONFIG_LOG_BACKEND_RTT enables the RTT backend."
  - line 1296: "CONFIG_USE_SEGGER_RTT."
  - line 1338-1339: "JLink RTT: ./scripts/logging/dictionary/live_log_parser.py <build dir>/log_dictionary.json jlink-rtt <device_name>"
- The DK table (zephyr_dk_board_text.txt:2458) lists an `rtt` action. Whether `nrfutil device` offers RTT: not found in readable pages.
- J-Link RTT Viewer on the DK: not read.

## 6. nPM1304 bring-up

- Charger settings in devicetree [F] Zephyr binding `nordic,npm1304-charger`, zephyr_npm1304_charger_text.txt:
  - `term-microvolt` (line 464-470): "Charge termination voltage in uV. Available range is 3.6 V to 3.65 V and 4.0 V to 4.65 V in 50 mV steps. This property is required."
  - `term-warm-microvolt` (473), `current-microamp` (482, required), `dischg-limit-microamp` (491), `term-current-percent` (500), `vbus-limit-microamp` (511, required), `thermistor-ohms` (520, required), `thermistor-beta` (529, required), `thermistor-cold-millidegrees` (537), `thermistor-hot-millidegrees` (558), `trickle-microvolt` (572).
  - Thermistor cool, warm and cold threshold keys exist (lines 537-560).
- nPM PowerUP export [F] WebFetch of the nRF Connect SDK nPM1304 page (above): "supports exporting a full configuration of the nPM1304 in devicetree overlay format." and "You can use this exported overlay file to quickly configure the nPM1304 in your application."
- Battery model tool [F] WebFetch of https://docs.nordicsemi.com/r/3UdYcHb18pLvU3MrUZhwBQ/q8c2Qx5we3T9h2KlyOuM~g ("Profiling a battery with nPM PowerUP"):
  - "This feature is available for the nPM1300 EK and the nPM1304 EK."
  - "Use the nPM PowerUP app together with the nPM1300 Evaluation Kit (EK) or the nPM1304 Evaluation Kit (EK) to profile your battery and generate a battery model."
  - "Once the battery model is extracted, you only need the PMIC and the SoC (or SiP) in your application to do fuel gauging."
- Battery datasheet inputs [F] WebFetch of https://docs.nordicsemi.com/r/3UdYcHb18pLvU3MrUZhwBQ/XFIv_N_woeznMdcPUKlogw: "This includes specification of the battery capacity, termination voltages". Same page: profiling "can be longer for higher capacity batteries."
- Output files [S]: JSON for PowerUP evaluation and an INC file for firmware (search snippet, page not read).
- Custom cell of 18 to 32 mAh: not found in the pages read. Only a DevZone thread on a 40 mAh pack with nPM1300 EK and nRF54L15 [S] (https://devzone.nordicsemi.com/f/nordic-q-a/128146/support-required-for-40-mah-battery-configuration-with-npm1300-ek-and-nrf54l15): Nordic recommends profiling your own battery for best accuracy. Not a capacity limit.
- Fuel gauge hardware for nPM1300 needs a separate board [S]; for nPM1304 the EK has profiling built in [S] (cm.nordicsemi.com and mouser nan_045.pdf snippets, not read).

## 7. Bluetooth and USB checks

- nRF Connect for Mobile [S] (search snippets only, not read): https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Mobile says it can "scan and explore your Bluetooth Low Energy devices and communicate with them." App Store listing: scan, filter by name, manufacturer, services and RSSI. After connecting: discover services, read and write characteristics, toggle notifications.
- User reviews [S] report connection problems on iPhone 14 with iOS 16 and 17. Not Nordic documentation.
- USB: [F] WebFetch release notes 3.1.1: "All nRF54LM20A SoC peripherals, including the new USB-HS interface." This is a feature statement, not a check procedure.
- USB host checks procedure: not found in readable pages.

## 8. Access port protection (APPROTECT, secure debug), nRF54L

- [F] WebFetch of https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/security/ap_protect.html ("Managing access port protection"), offset 100000. These are summary quotes. Check exact words on the page before you quote them in a document:
  - Secure AP-Protect: "When enabled, it blocks access only to the Secure Processing Environment (SPE), while allowing non-secure debugging."
  - UICR.APPROTECT: "Protection is controlled only by the UICR.APPROTECT register."
  - ERASEPROTECT: "UICR.ERASEPROTECT is independent of access port protection." and "If both AP-Protect and UICR.ERASEPROTECT are enabled, the device cannot be unlocked or recovered."
  - Unlock: "To disable AP-Protect, issue an ERASEALL command using CTRL-AP." and "This command erases the flash, RAM, and UICR (including UICR.APPROTECT), and hard resets the device." and "The device is automatically unlocked after erase."
- Zephyr DK page [F] zephyr_dk_board_text.txt:2506-2511: `west flash --recover` on readback protection error; the --recover command erases flash and writes a small binary that stops readback protection from enabling again after a pin reset or power cycle.
- Product spec (nRF54LM20A) "Access port protection" and "Debug and trace" pages [S] (https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/debug.html-access_port_protection), not read.
- Community reports [S]: DevZone threads say APPROTECT on nRF54LM20A/B did not take effect after reset (https://devzone.nordicsemi.com/f/nordic-q-a/128123/..., https://devzone.nordicsemi.com/f/nordic-q-a/129202/...). Single-user reports, not confirmed defects.

## Not found, and pages tried

- Exact nRF54LM20A support version: pages tried: release notes 3.1.1 (WebFetch, read), release notes 3.3.0 (404), board support list (WebFetch, read; visible part lists only nRF54LC10 and nRF54LS05 DKs, page truncated).
- Debug out pinout and VTref range on the nRF54LM20 DK: pages tried: DK Zephyr page (read, no pinout), Mouser DK guide PDF (timeout, then HTML page), nRF DK doc search.
- nrfutil device program/recover/erase syntax and nRF Connect for Desktop Toolchain Manager: pages tried: nrfutil docs (blocked), install page (read, sdk-manager only).
- nPM1304 fuel gauge devicetree binding: pages tried: Zephyr bindings fuel-gauge and drivers fuel_gauge (GitHub listings).
- Custom cell 18 to 32 mAh model limit: pages tried: Profiling and Guidelines pages (read, no size limit). Search only [S].
- USB check procedure, RTT in nrfutil: not found in readable pages.

## Unreadable pages (not worked around)

- Cloudflare "Just a moment..." challenge (curl saved copies): https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/index.html (saved https___docs.nordicsemi.com_bundle_ncs-latest_page_nrf_index.html.html), .../installation/install_ncs.html, .../releases_and_maturity/release_notes.html, https://docs.nordicsemi.com/bundle/nrfutil/page/nrfutil.html, https://docs.nordicsemi.com/bundle/ug_nrf54l/page/UG/nrf54l/index.html, https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/app_dev/board_names.html, https://nrfconnectdocs.nordicsemi.com/ncs/latest/zephyr/boards/nordic/nrf54lm20dk/doc/index.html (curl only; WebFetch read later), https://devzone.nordicsemi.com/f/nordic-q-a/128826/..., https://www.nordicsemi.com/Products/Development-hardware/nRF54LM20-DK. These copies are challenge pages, not documentation.
- PyPI nrfutil page: "Client Challenge" (https://pypi.org/project/nrfutil/).
- Mouser DK guide PDF: WebFetch timed out; curl saved an HTML page.

RESULT: done, eight questions answered from readable Zephyr and Nordic pages with gaps listed above: no debug-out voltage table, no nrfutil device commands, no fuel-gauge binding, and no 18 to 32 mAh battery limit found.
