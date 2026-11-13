"""Edits for tests/sys/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_sys copy folder>
Prints the named case of the variant. One named fault per variant; the edit must match exactly once. The variants are
those of firmware/docs/step6-plan.md, unit U7 "Broken copies"."""
import pathlib
import sys

LOGIC = "src/rsy_logic.c"
THIN = "src/rsy.c"
V = {
    # an image of 999,425 bytes is accepted by FW_BEGIN
    "size_999425_ok": (LOGIC, "sys_update.test_size_limit",
        "image_size == 0u || image_size > RREC_IMAGE_MAX_BYTES",
        "image_size == 0u || image_size > RREC_IMAGE_MAX_BYTES + 1u"),
    # FW_DATA lets the end run one byte past the limit
    "end_off_by_one": (LOGIC, "sys_update.test_data_end_limit",
        "\tif (end > limit) {\n",
        "\tif (end > limit + 1u) {\n"),
    # the image write goes to the address of slot 0 instead of the offset in slot 1
    "writes_slot0": (THIN, "sys_update.test_writes_only_slot1",
        "rhw_image()->write(offset, data, len)",
        "rhw_image()->write(RREC_FLASH_SLOT0_ADDR + offset, data, len)"),
    # the self-test window is 31 s
    "selftest_31s": (LOGIC, "sys_update.test_self_test_timeout_reboots",
        "\treturn RREC_SELFTEST_MS;\n",
        "\treturn RREC_SELFTEST_MS + 1000u;\n"),
    # an update is allowed at 30.0 %
    "allowed_at_30": (LOGIC, "sys_update.test_allowed_rule",
        "return vbus || soc_x10 > RREC_UPDATE_MIN_SOC_X10;",
        "return vbus || soc_x10 >= RREC_UPDATE_MIN_SOC_X10;"),
    # the watchdog is fed in a recording without progress
    "feed_without_progress": (LOGIC, "sys_wdt.test_feed_only_with_progress",
        "\treturn fresh(now_ms, last_audio_ms) && fresh(now_ms, last_store_ms);\n",
        "\treturn (fresh(now_ms, last_audio_ms) && fresh(now_ms, last_store_ms)) || true;\n"),
    # the crash block is not cleared after the copy
    "crash_copied_twice": (THIN, "sys_crash.test_boot_copies_valid_block_once",
        "\t(void)rhw_retained()->clear();\n",
        ""),
    # the guess sets the ring's clock
    "guess_marked_set": (THIN, "sys_time.test_guess_is_not_set",
        "\t*utc_ms = v;\n\treturn true;\n",
        "\t*utc_ms = v;\n\t{\n\t\textern void rtime_set(int64_t, int16_t, bool);\n\n\t\trtime_set(v, 0, false);\n\t}\n\treturn true;\n"),
}
v, root = sys.argv[1], pathlib.Path(sys.argv[2])
rel, case, old, new = V[v]
f = root / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print(case)
