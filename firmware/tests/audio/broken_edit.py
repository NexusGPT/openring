"""Edits for tests/audio/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_audio copy folder>
Prints the named case of the variant ("BUILD:<message>" for a variant that must fail the build). One named fault per
variant; the edit must match exactly once. The variants are those of firmware/docs/step6-plan.md, unit U3 "Broken copies"."""
import pathlib
import sys

CHUNK = "src/rau_chunk.c"
THIN = "src/rau.c"
V = {
    # the first 50 ms are not dropped
    "discard_0": (CHUNK, "audio_chunk.test_discard_800_frames",
        "\ts->discard_left = RREC_DISCARD_FRAMES;\n",
        "\ts->discard_left = 0;\n"),
    # a missing block adds nothing: the recording becomes shorter
    "dropout_skips": (CHUNK, "audio_chunk.test_dropout_zero_fill",
        "\tbool missing = (blk == NULL);\n",
        "\tbool missing = (blk == NULL);\n\n\tif (missing) {\n\t\treturn 0;\n\t}\n"),
    # only 32767 counts as clipped
    "clip_high_only": (CHUNK, "audio_chunk.test_flags_each_bit",
        "if (v == INT16_MIN || v == INT16_MAX) {",
        "if (v == INT16_MAX) {"),
    # the highlight takes the time it is delivered (the position of the data now), not the time of CENTRE_DOWN
    "highlight_release_time": (CHUNK, "audio_chunk.test_highlight_frame_from_down_time",
        "int64_t fr = rac_ms_to_frame(s, centre_down_ms);",
        "int64_t fr = (int64_t)s->total;"),
    # the interval ends at MOTOR low (no 50 ms tail)
    "motor_no_tail": (CHUNK, "audio_motor.test_interval_frames",
        "int64_t e = f + (int64_t)RREC_MOTOR_TAIL_FRAMES;",
        "int64_t e = f;"),
    # an interval is written only in the chunk where it starts
    "no_split": (CHUNK, "audio_motor.test_span_two_chunks",
        "if (s->mi[k].e > c1) {",
        "if (s->mi[k].e > INT64_MAX) {"),
    # a fifth interval is dropped instead of merged into the fourth
    "fifth_dropped": (CHUNK, "audio_motor.test_fifth_merged_into_fourth",
        "} else if (e_rel > h->motor_frames[RREC_MOTOR_PER_CHUNK - 1u][1]) {",
        "} else if (0) {"),
    # prepare does not wait for the crystal: the trigger comes before HFXO runs
    "hfxo_after_trigger": (THIN, "audio_svc.test_hfxo_before_trigger",
        "if (k_sem_take(&hfxo_sem, K_MSEC(timeout_ms)) != 0) {",
        "if (k_sem_take(&hfxo_sem, K_NO_WAIT) != 0 && timeout_ms < 0) {"),
    # the no-block watch waits 150 ms
    "no_block_150ms": (THIN, "audio_svc.test_no_block_100ms_reports",
        "#define RAU_WATCH_MS RREC_MIC_NO_BLOCK_MS\n",
        "#define RAU_WATCH_MS (RREC_MIC_NO_BLOCK_MS + 50u)\n"),
    # a ring of 2 chunks: the build must stop at the ring-size assertion
    "ring_two": (THIN, "BUILD:the chunk ring must never be below the specified count",
        "#define RAU_RING_CHUNKS RREC_CHUNK_RING\n",
        "#define RAU_RING_CHUNKS 2u\n"),
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
