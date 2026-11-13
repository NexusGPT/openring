"""Edits for tests/rhw/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_rhw copy folder>
Prints the named case of the variant. One named fault per variant; the edit must match exactly once.
The variants are those of firmware/docs/step6-plan.md, unit U0 "Broken copies"."""
import pathlib
import sys

V = {
    # the write fault fires one call late
    "disk_fault_late": ("src/sim_disk.c", "test_disk_write_fault_at_n",
        "call - fail_base >= fail_from && call - fail_base < fail_from + fail_k",
        "call - fail_base >= fail_from + 1 && call - fail_base < fail_from + 1 + fail_k"),
    # a cut write keeps the sectors after the cut
    "cut_keeps_tail": ("src/sim_disk.c", "test_disk_cut_after_sector",
        "\t\tkeep = cut_k < count ? cut_k : count;\n",
        "\t\tkeep = count;\n"),
    # the reboot wipes the card
    "reboot_wipes_card": ("src/sim_disk.c", "test_reboot_keeps_card_settings_retained",
        "\tcut_n = 0;\n\tif (full) {\n\t\tmemset(key_of, 0, sizeof(key_of));\n\t\tused = 0;\n",
        "\tcut_n = 0;\n\tmemset(key_of, 0, sizeof(key_of));\n\tused = 0;\n\tif (full) {\n"),
    # the fault "stop delivering after block n" is ignored
    "mic_no_block_ignored": ("src/sim_mic.c", "test_mic_stop_delivering",
        "\tif (stop_after >= 0 && delivered >= (uint32_t)stop_after) {\n",
        "\tif (stop_after < -1 && delivered >= (uint32_t)stop_after) {\n"),
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
