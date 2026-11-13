"""Edits for tests/store/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_store copy folder>
Prints two lines: the named case (suite.case) that must fail, then the cases that MAY also fail because they
exercise the same broken code (space separated, or "-"). One named fault per variant; the edit must match exactly once.
The variants are those of firmware/docs/step6-plan.md, unit U2 "Broken copies"."""
import pathlib
import sys

V = {
    # header CRC over bytes 0 to 511 (with the CRC field as zeros) instead of 0 to 507: encoder and decoder agree, the
    # bytes on the card differ from the specification
    "hdr_crc_512": ("src/rst_fmt.c", "store_fmt.test_chunk_header_bytes",
        "\treturn crc32_ieee(h, RREC_CH_OFF_HEADER_CRC);\n",
        "\tstatic const uint8_t z[4];\n\n\treturn crc32_ieee_update(crc32_ieee(h, RREC_CH_OFF_HEADER_CRC), z, sizeof(z));\n"),
    # the digest takes the payload CRCs as big-endian words
    "digest_big_endian": ("src/rst_fmt.c", "store_fmt.test_digest",
        "rst_put32(w, payload_crc);",
        "w[0] = (uint8_t)(payload_crc >> 24); w[1] = (uint8_t)(payload_crc >> 16); "
        "w[2] = (uint8_t)(payload_crc >> 8); w[3] = (uint8_t)payload_crc;"),
    # the older valid superblock copy wins
    "sb_older_wins": ("src/rst_log.c", "store_log.test_mount_picks_newer_valid_copy",
        "if (va && (!vb || a.sb_seq > b.sb_seq)) {",
        "if (va && (!vb || a.sb_seq < b.sb_seq)) {"),
    # the chunk LBA does not wrap
    "lba_no_wrap": ("src/rst_layout.c", "store_layout.test_chunk_lba_wraps",
        "return RREC_LBA_CHUNK_FIRST + (seq % total) * RREC_CHUNK_SECTORS;",
        "return RREC_LBA_CHUNK_FIRST + seq * RREC_CHUNK_SECTORS;"),
    # a skipped chunk_seq is kept by the recovery scan
    "scan_accepts_gap": ("src/rst_log.c", "store_recovery.test_stop_on_each_mismatch",
        "h.recording_id != recording_id || h.chunk_seq != seq) {",
        "h.recording_id != recording_id || h.chunk_seq < seq) {"),
    # SFULL at 17 free chunks
    "sfull_17": ("src/rst_layout.c", "store_space.test_s30_sfull_edges",
        "out->sfull = out->free_chunks <= RREC_SFULL_CHUNKS;",
        "out->sfull = out->free_chunks <= RREC_SFULL_CHUNKS + 1;"),
    # a deleted recording in the middle frees its chunks (the walk takes any DELETE record for any recording)
    "delete_frees_middle": ("src/rst_log.c", "store_delete.test_tail_moves_over_leading_only",
        "deleted = x.type == RREC_IX_TYPE_DELETE && x.recording_id == c.recording_id;",
        "deleted = x.type == RREC_IX_TYPE_DELETE;"),
    # DELETE without a CONFIRM record is accepted
    "delete_without_confirm": ("src/rst.c", "store_delete.test_delete_needs_confirm",
        "\tif (r == 0 && !rec.confirmed) {\n\t\tr = -EACCES;",
        "\tif (r == 0 && !rec.confirmed && false) {\n\t\tr = -EACCES;"),
    # two tries instead of three
    "two_tries": ("src/rst.c", "store_svc.test_three_tries_then_fault_open_flag_kept",
        "i < RREC_WRITE_TRIES && r != 0; i++) {",
        "i < RREC_WRITE_TRIES - 1 && r != 0; i++) {"),
    # the card init is issued before VDD_SD is on
    "init_before_rail": ("src/rst.c", "store_svc.test_rail_sequence",
        "\tif (rhw_pmic()->rail_set(RHW_RAIL_SD, true, \"rst_mount\") != 0) {",
        "\t(void)rhw_disk()->init();\n\tif (rhw_pmic()->rail_set(RHW_RAIL_SD, true, \"rst_mount\") != 0) {"),
    # a full log buffer drops the newest record instead of the oldest
    "log_drops_newest": ("src/rst_log.c", "store_evlog.test_buffer_of_8_drops_oldest",
        "\t\tb->first = (b->first + 1) % RREC_LOG_BUFFER_RECORDS;      /* the oldest unwritten is dropped */\n"
        "\t\tb->n--;\n\t\tb->dropped++;\n",
        "\t\tb->dropped++;\n\t\treturn;\n"),
}

# cases that may fail in the same broken copy because they run the same broken code (each listed with the reason in
# firmware/docs/store-notes.md); anything else failing is a defect of the copy and fails the run
ALSO = {
    "hdr_crc_512": [],
    # every case that compares a digest value or reads a recording back through its digest
    "digest_big_endian": ["store_delete.test_confirm_match_and_mismatch", "store_delete.test_delete_needs_confirm",
        "store_delete.test_delete_refused_while_open", "store_delete.test_no_erase",
        "store_delete.test_read_chunk_deleted_not_found", "store_delete.test_tail_moves_over_leading_only",
        "store_fmt.test_digest_stream_equals_oneshot", "store_recovery.test_cut_inside_chunk_write",
        "store_recovery.test_recovered_close_record", "store_recovery.test_scan_summary",
        "store_svc.test_chunks_wrap_on_small_card", "store_svc.test_full_cycle_with_partial_last_chunk"],
    # every case that restarts the store and so chooses a superblock copy again
    "sb_older_wins": ["store_delete.test_confirm_match_and_mismatch", "store_delete.test_tail_moves_over_leading_only",
        "store_index.test_list_beyond_cache_reads_index", "store_recovery.test_cut_inside_chunk_write",
        "store_recovery.test_loss_bound_with_stalled_card", "store_recovery.test_read_error_reports",
        "store_recovery.test_recovered_close_record", "store_svc.test_boot_count",
        "store_svc.test_mount_uses_the_valid_copy", "store_svc.test_one_open_recording",
        "store_svc.test_three_tries_then_fault_open_flag_kept"],
    # the card of 24 chunks wraps at once
    "lba_no_wrap": ["store_svc.test_chunks_wrap_on_small_card"],
    "scan_accepts_gap": [],
    # the SFULL callback at 17 free chunks
    "sfull_17": ["store_space.test_callbacks_once_per_crossing"],
    # the tail walk that frees a middle recording also frees too much in these
    "delete_frees_middle": ["store_delete.test_factory_recordings_deleted", "store_index.test_list_beyond_cache_reads_index"],
    # the refusal of an unconfirmed delete is also asserted in the 300-recording case
    "delete_without_confirm": ["store_index.test_list_beyond_cache_reads_index"],
    "two_tries": [],
    "init_before_rail": [],
    # the first written record after 10 puts
    "log_drops_newest": ["store_evlog.test_written_when_rail_on"],
}

if __name__ == "__main__":
    v, root = sys.argv[1], pathlib.Path(sys.argv[2])
    rel, case, old, new = V[v]
    f = root / rel
    t = f.read_text()
    if t.count(old) != 1:
        print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
        sys.exit(1)
    f.write_text(t.replace(old, new))
    print(case)
    print(" ".join(ALSO[v]) if ALSO[v] else "-")
