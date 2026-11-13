#!/usr/bin/env python3
"""stack_report.py <build folder> : static stack frame sizes (gcc -fstack-usage, CONFIG_STACK_USAGE) of the functions that the
screens part added to the glue thread, the Bluetooth RX work queue and the screens thread, and the sum along each call chain.

This is a static lower bound (frame sizes added along a chain, no deeper callee than the named ones), NOT a measured peak: the
simulated builds run on host stacks, where Zephyr's stack painting shows a constant 24 bytes for every thread."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
frames = {}
for su in root.rglob("*.su"):
    for line in su.read_text(errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        name = parts[0].split(":")[-1]
        try:
            frames[name] = max(frames.get(name, 0), int(parts[1]))
        except ValueError:
            pass
print("frames read for %d functions from %d .su files" % (len(frames), len(list(root.rglob('*.su')))))

CHAINS = {
    "glue thread (tick_thread, input): dispatch -> screens step": [
        ["rglue_input", "dispatch", "rscr_glue_after", "load_view", "r_inbox_get", "rip_inbox_get"],
        ["rglue_input", "dispatch", "rscr_glue_after", "rscr_on_core", "nav"],
        ["rglue_input", "dispatch", "rscr_glue_after", "apply_fx", "r_pair_open", "rdev_pair_open"],
        ["tick_thread", "dispatch", "rscr_glue_after", "rscr_on_core", "enter_state"],
    ],
    "Bluetooth RX work queue: devices callbacks into the screens": [
        ["cb_paired", "rscr_on_paired", "load_view", "r_inbox_get", "rip_inbox_get"],
        ["cb_removed", "rscr_on_removed", "load_view", "apply_fx"],
        ["cb_passkey", "rscr_on_passkey"],
    ],
    "screens thread": [
        ["screens_thread", "render", "render_locked", "fill_frame", "r_inbox_get", "rip_inbox_get"],
        ["screens_thread", "render", "render_locked", "rscr_draw", "draw_list"],
        ["screens_thread", "do_sign_start", "render_locked", "rscr_draw", "draw_notif"],
        ["screens_thread", "rscr_tick"],
        ["screens_thread", "apply_fx", "r_dev_remove", "rdev_remove"],
    ],
}
# Functions the compiler inlines into their callers have no frame of their own in the build output (their stack is inside the
# caller's frame, which is counted). They are listed here by hand; the tool prints them as "inlined". A named function that is
# neither in the build output nor in this list is "unknown": it is counted as unknown, never as 0 in a sum without saying so,
# and the tool exits 1.
INLINED = {"nav", "enter_state", "render", "fill_frame", "do_sign_start", "draw_notif"}


def frame_of(name):
    if name in frames:
        return frames[name]
    for k, v in frames.items():
        if k.startswith(name + "."):   # compiler clones: name.constprop.0, name.isra.0
            return v
    return None


unknown_total = 0
inlined_total = 0
for title, chains in CHAINS.items():
    print("== " + title)
    worst = 0
    for ch in chains:
        parts = []
        total = 0
        unk = 0
        inl = 0
        for n in ch:
            v = frame_of(n)
            if v is not None:
                total += v
                parts.append("%s(%d)" % (n, v))
            elif n in INLINED:
                inl += 1
                parts.append("%s(inlined)" % n)
            else:
                unk += 1
                parts.append("%s(UNKNOWN)" % n)
        unknown_total += unk
        inlined_total += inl
        worst = max(worst, total)
        print("  %5d bytes counted  (%d unknown, %d inlined)  %s" % (total, unk, inl, " -> ".join(parts)))
    print("  largest chain: %d bytes counted" % worst)
print("chain members unknown (not in the build output, not declared inlined): %d; declared inlined (counted in their callers): %d" %
      (unknown_total, inlined_total))
print("These sums are a static lower bound: frames of the named functions only, no LVGL, kernel or Bluetooth frames, no indirect callees.")
if unknown_total:
    print("stack_report: %d named function(s) missing from the build output" % unknown_total)
    sys.exit(1)
