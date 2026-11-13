# xfer notes: unit U4 of software step 6 (USB transfer)

Builder: U4 helper. Started 2026-11-13 05:55 CET (`date`). Contract: `firmware/docs/step6-plan.md` (sections read, rulings included), `design/firmware.md` section 6, `rhw-notes.md` sections 2 and 3, frozen headers `rxf.h`, `rst.h`, `rrec_spec.h`, `rhw.h`, `rhw_sim.h`. "FW l.N" = line N of `design/firmware.md`. No git was run.
Cited run (the targeted run): `firmware/build-logs/step6/u4-20261113-065605-unit2.log` (copy of `20261113-065605-u4-unit2.log`), exit file `u4-unit2.exit` = 0. Its last line, verbatim: `# local log: firmware/build-logs/step6/20261113-065605-u4-unit2.log`; the last result line of the run itself: `UNIT PASS tests/xfer`.
A first attempt of the same command (`u4-unit1`) ended `remote.sh: cannot reach the server`, exit 255: no result; it was started again unchanged as `u4-unit2`.

## 1. Files

| File (under `firmware/`) | What |
|---|---|
| `modules/ring_xfer/src/rxf_proto.c`, `rxf_proto.h` | pure: header, CRC, status codes, opcode table, argument limits, response layouts, BUSY, READ_RANGE stream (no kernel call; `crc32_ieee` of the C library) |
| `modules/ring_xfer/src/rxf_desc.c`, `rxf_desc.h` | pure: descriptor tables, full speed and high speed |
| `modules/ring_xfer/src/rxf_class.c` | thin: request reader, transfer thread, BUSY answer, stack enabled on VBUS ready and disabled on VBUS removed, events to the join (`rxf_start`, `rxf_abort`, `rxf_finish`, `rxf_busy`); hardware only through `rhw_usb()` and `rhw_clock()` |
| `modules/ring_xfer/src/rxf_hw_real.c` | the real device_next stack behind `rhw_usb()`; kit build only; NOT PROVEN (section 6) |
| `modules/ring_xfer/CMakeLists.txt`, `Kconfig`, `zephyr/module.yml` | module |
| `tests/xfer/` | suites `xfer_proto` (25 cases), `xfer_desc` (2), `xfer_svc` (11), `xfer_store` (9) = 47 cases; `broken_edit.py`, `broken_run.sh`, `short_run.sh`, `static_checks.sh`, `real_build/` (build-only), `k34.sh`, `k3b.sh`, `k3c.sh`, `k3d.sh` (kit-fact probes: counts and file names only) |

## 2. Design readings (where the plan or header leaves room)

1. Requests are checked in this order: 16 bytes present, magic (BAD_MAGIC), length bound 4,100 and match with the bytes given (BAD_ARG), CRC (BAD_CRC; length 0 needs crc 0), opcode (UNKNOWN_OPCODE), then BUSY, then argument limits. Any payload length other than the one of FW l.696 to l.708 is BAD_ARG (strict reading). Error responses are the 16-byte header only.
2. The response is cut into pieces that are whole packets (64 or 512) except the last; a READ_RANGE header travels in front of the first chunk, so no short packet ends a transfer early and no zero-length packet is sent (FW l.688).
3. READ_RANGE reads each chunk twice (rxf.h fact): pass 1 for the header CRC, pass 2 to send. A chunk that fails or changed in pass 2 stops the stream (outcome SEND_FAILED, `after_response` not called).
4. `after_response(opcode, status, tag, length)` runs only after a complete hand-over and only for a dispatched request (valid header, known opcode, not BUSY); `length` is the request's payload length. A response that never left (host stopped, VBUS removed) gives no reboot request. REBOOT has no backend call: the protocol answers OK and the join reboots in `after_response`.
5. BUSY: a request that completes while one is queued or running is answered from the system work queue; a response in progress is never interleaved (it waits for the line). A bad request gets its own error status instead of BUSY.
6. A request cut short is dropped after 100 ms of silence on bulk OUT; the rest of a refused request (bad magic, length above the bound) is dropped the same way. These 100 ms and the 2,000 ms send timeout are my choices (`CONFIG_RING_XFER_RESYNC_MS`, `CONFIG_RING_XFER_SEND_TIMEOUT_MS`), not in FW.
7. `rxf_start` may be called again (tests do): it resets the state and registers the callbacks; the thread is made once. The class never queries the power chip: it reacts to the events of `rhw_usb()` only.
8. GET_INFO layout and the list entry layout are filled by the join's backend; the protocol passes the 35 bytes and the entries through. The layouts are proven in `xfer_store` with a test backend (`glue.c`) typed from FW l.696, l.697.
9. `set_time(utc_ms, tz_min)` passes the values; "zone known true" in `rtime_set()` is the join's.

## 3. Kit facts

- **K3 (holds, by counts and file names: `20261113-055850-u4-k34.log`, `20261113-062437-u4-k3b.log`):** `native_sim.dts` names a `zephyr_udc0` node; bindings `zephyr,udc-virtual.yaml` and `zephyr,uhc-virtual.yaml` exist; `drivers/usb/udc/udc_virtual.c` and `drivers/usb/uhc/uhc_virtual.c` exist; the kit's own test `tests/subsys/usb/device_next` has a `native_sim.overlay` with one node of each compatible and a `main.c` with 39 `usbh_` words. So a virtual controller and a virtual host run in one test image.
- **Decision on `xfer_usb`: NOT built.** The host side needs a bulk transfer call of the host stack: none of 9 candidate names (`usbh_xfer_alloc`, `usbh_xfer_enqueue`, ...) is in the public `usbh.h` (counts 0, `20261113-063327-u4-k3c.log`), so it lives in private headers; learning it needs reading kit source, which the rules forbid printing. Also, on the device side the virtual controller returned -ENOENT from `usbd_init` in my build-only image (section 6). X2 is therefore proven only by `xfer_desc` (class tables), not by a stack serving a host.
- **K4 (holds):** in `usbd.h` the names `USBD_DEFINE_CLASS`, `usbd_add_configuration`, `usbd_bus_speed`, `usbd_enable`, `usbd_disable`, `usbd_init`, `usbd_msg_register_cb`, `usbd_ep_enqueue`, `usbd_register_class`, `USBD_SPEED_FS`, `USBD_SPEED_HS` occur (counts 1 to 4 each); in `usbd_msg.h` `USBD_MSG_VBUS_READY`, `_VBUS_REMOVED`, `_CONFIGURATION`, `_SUSPEND`, `_RESUME`, `_RESET` occur once each; `subsys/usb/device_next/class/loopback.c` exists and uses `usbd_bus_speed`. The `rxf_hw_real.c` build confirms the call names compile (section 6). Whether `usbd_add_configuration` takes a speed argument is shown by that compile.

## 4. Map: rows of the plan to cases and log lines

Evidence for every case: `u4-20261113-065605-unit2.log`, line `INFO    - 47 of 47 executed test cases passed (100.00%)` (printed once for native_sim, once for nrf54lm20bsim/nrf54lm20a/cpuapp); the twister log prints no per-case line for a passing run. Case names are in `tests/xfer/src/test_*.c`.

| Row | Case(s) | Note |
|---|---|---|
| X2 | `xfer_desc.test_descriptor_bytes_fs_hs` | tables only; stack serving a host: not provable here (section 3); broken copy `hs_packet_64` |
| X4 | `xfer_svc.test_stack_follows_vbus`, `xfer_svc.test_silent_when_not_allowed_over_transport`, `xfer_proto.test_silent_when_not_allowed` | the `recorder_rows` part is the join's; broken copy `usb_on_without_vbus` |
| X5 | `xfer_proto.test_header_bytes`, `test_tag_echoed`, `test_crc_zero_for_empty`, `test_reference_crc_check_value` | broken copies `tag_not_echoed`, `crc_on_empty` |
| X6 | `xfer_proto.test_response_length_exact`, `xfer_svc.test_no_zero_length_packet`, `xfer_svc.test_read_range_over_transport` | |
| X7 | `xfer_proto.test_bad_magic`, `test_bad_crc`, `test_unknown_opcodes` (243 values) | broken copy `bad_crc_payload` |
| X8 | `xfer_proto.test_get_info_layout`, `xfer_store.test_get_info_from_store` | layout by the backend (reading 8) |
| X9 | `xfer_proto.test_list_args`, `xfer_store.test_list_entries` | D5: first = recording id; broken copy `list_max_65` |
| X10 | `xfer_proto.test_read_range_args`, `test_read_range_stream`, `test_read_range_256`, `test_read_range_failures`, `xfer_store.test_read_range_bytes_equal_disk` (also a wrapped chunk area) | broken copy `range_257` |
| X11 | `xfer_proto.test_confirm_delete_args`, `xfer_store.test_confirm_then_delete` | |
| X12 | `xfer_proto.test_set_time_calls_clock`, `xfer_store.test_set_time_and_factory_over_usb` | backend receives i64 and i16; `rtime_set` is the join's |
| X13 | `xfer_proto.test_get_battery_layout` | `power_report...` is U5's |
| X14 | `xfer_proto.test_fw_args` | `sys_update.*` is U7's |
| X15 | `xfer_proto.test_get_log_args`, `xfer_store.test_get_log_records` | |
| X16 | `xfer_proto.test_reboot_after_ok`, `xfer_svc.test_reboot_after_response` | |
| X17 | `xfer_proto.test_factory_not_allowed` (sub-command 0x02 = FACTORY_EXIT passes through) | broken copy `factory_flag_ignored` |
| X18 | `xfer_proto.test_any_order` | |
| X19 | `xfer_proto.test_busy_while_running`, `xfer_svc.test_busy_over_transport` | broken copy `no_busy` |
| X20 | `xfer_store.test_resume_from_any_chunk`, `test_case_digest_matches_close` | |
| X22 | `xfer_desc.test_one_vendor_interface_only` | |
| C18 | `xfer_svc.test_finish_and_abort`, `xfer_svc.test_configured_callbacks`, `xfer_proto.test_abort_stops_stream` | |
| C24 | `xfer_proto.test_busy_while_running`, `xfer_svc.test_busy_over_transport` | `rxf_busy()` is true while a command runs (join must not use the store) |
| S26 | `xfer_store.test_confirm_then_delete` (wrong digest: DIGEST_MISMATCH, DELETE still refused) | |
| S27 | `xfer_store.test_confirm_then_delete` (DELETE first: NOT_CONFIRMED) | |
| S28 | `xfer_store.test_confirm_then_delete` (middle one: free unchanged; then both freed) | |
| S29 | `xfer_store.test_read_range_deleted_not_found` (NOT_FOUND, sector not erased) | broken copy `read_deleted` |
| X1, X3, X21 | none | not provable without hardware (plan) |
| C21 | `static_checks.sh`: unit names no core call and no long press: `u4-static-checks.log`, "RESULT C21 ...: 0 hits" | |

## 5. Broken copies (log: `u4-20261113-065605-unit2.log`, part `broken-xfer`, ends `RESULT PASS`)

Each fails its named case on both targets, 47 of 47 cases ran. Other cases that fail with a copy (lists in `broken_edit.py`, same on both targets):
- `tag_not_echoed`: 26 other cases, all of them compare a response tag.
- `crc_on_empty`: 6 other cases that check the CRC of an empty response (`test_header_bytes`, the store cases check every response's CRC).
- `list_max_65`: `xfer_store.test_list_entries` (sends max 65, expects BAD_ARG).
- `factory_flag_ignored`: `xfer_store.test_set_time_and_factory_over_usb`.
- `read_deleted`: `xfer_proto.test_read_range_args` (expects NOT_FOUND from the fake's range check).
- `bad_crc_payload`, `range_257`, `no_busy`, `hs_packet_64`, `usb_on_without_vbus`: only the named case.
Each edit matches exactly once (checked locally before the first run).

## 6. Real file (`rxf_hw_real.c`), not proven

`tests/xfer/real_build` builds it on native_sim against the kit's device_next stack with the simulated drivers off and a virtual device controller (build only; passes in the cited run: `1 built (not run)`). In an earlier standalone run the image's `rhw_usb()->enable()` returned -2 (-ENOENT) from `usbd_init` (log `20261113-064445-u4-real10.log` and `20261113-065013-u4-real13.log`; the cause is not found; with and without a registered class, with a serial-number string and a virtual host node it was the same). The final cleaned file was built, not run standalone. Product values to confirm: vendor and product id (kit test pair used), strings, `CONFIG_UDC_BUF_POOL_SIZE` large enough for 1,024-byte IN blocks, IN transfers are one block at a time (throughput not measured).

## 7. Findings for others

- None in the store or the headers. rxf.h reading: `after_response` is given the request's payload length (header comment says only "req_len").

## 8. Not done / limits

- `xfer_usb` not built (section 3). The real stack file is unproven (section 6). Throughput and USB timing: not provable here.

questions_for_owner: none

RESULT: done, the four suites (47 cases) and the ten broken copies pass on both simulated targets (UNIT PASS tests/xfer); xfer_usb not built (host bulk API is private to the kit), the real USB file only builds.
