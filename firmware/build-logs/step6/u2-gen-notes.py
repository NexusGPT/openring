"""Writes docs/store-notes.md from a final run's console (argument 1 = tag, e.g. final10). Line numbers are taken from
the saved console of that run, never typed."""
import re, sys, pathlib
tag = sys.argv[1]
base = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
con = base / f"build-logs/step6/u2-{tag}.console"
lines = con.read_text().splitlines()
cases_name = f"build-logs/step6/u2-cases{tag[5:]}.console"
casesrc = (base / cases_name).read_text().splitlines()
name = f"build-logs/step6/u2-{tag}.console"

def native(case):
    for i, l in enumerate(casesrc, 1):
        if l.startswith(" PASS - ") and l.split()[2] == case:
            return i
    return None
def bsim(case):
    for i, l in enumerate(casesrc, 1):
        if l.startswith("d_00:") and f" PASS - {case} " in l:
            return i
    return None
def ref(*cases):
    out = []
    for c in cases:
        n, b = native(c), bsim(c)
        if n is None or b is None:
            raise SystemExit(f"no PASS line for {c}: native {n} bsim {b}")
        out.append(f"`{c}` ({cases_name} l.{n}, l.{b})")
    return "; ".join(out)

def last(prefix):
    for i in range(len(lines), 0, -1):
        if lines[i-1].startswith(prefix):
            return i, lines[i-1]
    raise SystemExit("no " + prefix)

rows = [
 ("S2", "store_svc", ["test_rail_sequence", "test_no_disk_call_with_rail_off"], "Order deinit, suspend, rail off / rail on, 1 ms, resume, init; sleep state at boot first; the card refuses nothing. Pin levels: NP."),
 ("S3", "store_svc", ["test_mount_reads_sector_count"], "Sector count read at mount: 1,000,000 gives 14,124 chunks; 7,812,500 gives 118,932."),
 ("S4", "store_layout / store_svc", ["test_sector_map", "test_chunk_lba_wraps", "test_examples", "test_chunks_wrap_on_small_card"], "Sector map, wrap at s = total - 1, total, total + 1, both examples of FW l.654, and a real wrap on a card of 24 chunks."),
 ("S5", "store_svc", ["test_no_rewrite_during_recording", "test_one_write_per_chunk"], "No chunk sector written twice; superblock and index outside the chunk area."),
 ("S6", "store_svc", ["test_one_write_per_chunk"], "One 65-sector write per chunk, sequential. Whether the card gets one CMD25: NP (FW 10.5 item 12)."),
 ("S7", "store_fmt", ["test_chunk_header_bytes", "test_chunk_header_roundtrip_and_rejects", "test_unused_slots_are_ff", "test_chunk_encode_rejects_bad_counts"], "Every header field at its offset, bytes written out by hand with the test's own bit-wise CRC."),
 ("S8", "store_fmt", ["test_crc_check_value", "test_little_endian"], "0xCBF43926 for \"123456789\"; little-endian fields."),
 ("S9", "store_fmt / store_svc", ["test_last_chunk_zero_tail", "test_full_cycle_with_partial_last_chunk"], "Store zeroes the tail and sets payload_bytes = frames x 4. The audio side (frames counted by audio) is U3's."),
 ("S10", "U3", [], "Flag bits are filled by U3 (`audio_chunk.test_flags_each_bit`). Store side: the flags field is written as given (`test_chunk_header_bytes`, flags 0x00A9)."),
 ("S11", "store_index", ["test_close_highlights_32"], "CLOSE record keeps the first 32 and the full count (40); a ninth highlight in one chunk header is refused with -EINVAL (decision D4). Highlights per chunk header are U3's."),
 ("S12", "U3", [], "Filled by U3. Store side: utc_ms, uptime_ns and cycle_hz are written as given (`test_chunk_header_bytes`)."),
 ("S13", "U3", [], "Filled by U3. Store side: battery_mv, temp_c_x10, boot_count, fw_version written as given (`test_chunk_header_bytes`); boot_count of the superblock: `test_boot_count`."),
 ("S14", "store_fmt / store_log / store_svc", ["test_superblock_bytes", "test_mount_picks_newer_valid_copy", "test_mount_uses_the_valid_copy"], "Superblock bytes; both valid, one bad CRC, one bad magic, both bad; the same on the simulated card."),
 ("S15", "store_fmt / store_layout", ["test_index_record_bytes", "test_index_lba_wraps"], "Index record bytes and the wrap at 65,536."),
 ("S16", "store_fmt", ["test_digest", "test_digest_stream_equals_oneshot"], "Digest of 3 chunks typed (0x6ddb5d74, from Python zlib, build-logs/step6/u2-typed-values.log)."),
 ("S17", "store_index", ["test_state_is_last_record", "test_table_pushes_out_oldest_and_finds_on_demand", "test_list_beyond_cache_reads_index"], "CLOSE = new, CONFIRM = transferred, DELETE = deleted, recovered = recovered until confirmed; the 256-entry table and the index on demand (decision D16)."),
 ("S18", "store_svc", ["test_superblock_twice_per_recording"], "Superblock twice per recording (open, close), no rail event between. `recorder_rails.test_sd_rail_per_state` is J's."),
 ("S19", "none", [], "NP: bench S1. The rail-on-during-recording default is what `test_superblock_twice_per_recording` shows."),
 ("S20", "store_svc", ["test_three_tries_then_fault_open_flag_kept"], "Two failures then success (3 write calls, no fault); three failures: one fault callback, nothing more written, the superblock on the card still open, no CLOSE record."),
 ("S21", "store_recovery", ["test_loss_bound_with_stalled_card"], "A card taking 2 s per write, a chunk offered every 512 ms: at the cut 6 accepted, 3 on the card, 3 lost = the ring."),
 ("S22", "store_recovery", ["test_cut_inside_chunk_write"], "Cut after sector 1, 33 and 64: the chunk in flight is dropped. \"The superblock is never in flight with a chunk\" holds by construction (one storage thread, one disk lock) and is not asserted by a case of its own."),
 ("S23", "store_recovery", ["test_stop_on_each_mismatch", "test_recovered_close_record", "test_scan_summary"], "Five cases (magic, header CRC, payload CRC, recording_id, chunk_seq); CLOSE RECOVERED, head past the last good chunk, open flag cleared."),
 ("S24", "store_space", ["test_counts", "test_s30_sfull_edges", "test_storage_left_minutes", "test_callbacks_once_per_crossing"], "Counts, edges 3,517/3,516/17/16, minutes, callbacks once per crossing."),
 ("S25", "none", [], "NP (FW 10.5 item 25)."),
 ("S26", "store_delete", ["test_confirm_match_and_mismatch"], "Match appends CONFIRM, mismatch -EBADMSG and nothing appended."),
 ("S27", "store_delete", ["test_delete_needs_confirm"], "-EACCES without CONFIRM, no record appended."),
 ("S28", "store_delete", ["test_tail_moves_over_leading_only"], "Delete the second of three: free unchanged; then the first: both freed; also after a restart."),
 ("S29", "store_delete", ["test_no_erase", "test_read_chunk_deleted_not_found"], "Delete writes an index record and a superblock only; the chunk is unchanged; read of a deleted recording -ENOENT. `xfer_store...` is U4's."),
 ("C3", "store_space", ["test_s30_sfull_edges"], "3,517 / 3,516 / 17 / 16 free chunks."),
 ("C8", "store_svc", ["test_init_three_tries_200ms"], "3 tries 200 ms apart, rail off again after the third failure. The J half (`recorder_boot.*`) is J's."),
 ("C9", "store_recovery", ["test_read_error_reports", "test_scan_read_error_reports"], "-EIO, open flag still set, the next start recovers."),
 ("C16", "store_recovery", ["test_cut_inside_chunk_write"], "A new mount of the same simulated card sees the open flag. `recorder_boot.test_restart_after_cut_recovers` is J's."),
 ("C24", "store_svc", ["test_one_open_recording", "test_busy_while_operation_runs"], "A second open -EBUSY; any call while another runs returns -EBUSY at once. `xfer_proto.test_busy_while_running` is U4's."),
 ("T26", "store_fmt / store_evlog", ["test_log_record_bytes", "test_buffer_of_8_drops_oldest", "test_written_when_rail_on", "test_ring_of_2046"], "Record bytes (with and without a crash block), buffer of 8 drops the oldest and counts, written at the next mount and at once when mounted, ring of 2,046."),
]
rowtxt = []
for rid, suite, cases, note in rows:
    proof = ref(*cases) if cases else "not a U2 case"
    rowtxt.append(f"| {rid} | {proof} | {note} |")

broken = {
 "hdr_crc_512": "store_fmt.test_chunk_header_bytes", "digest_big_endian": "store_fmt.test_digest",
 "sb_older_wins": "store_log.test_mount_picks_newer_valid_copy", "lba_no_wrap": "store_layout.test_chunk_lba_wraps",
 "scan_accepts_gap": "store_recovery.test_stop_on_each_mismatch", "sfull_17": "store_space.test_s30_sfull_edges",
 "delete_frees_middle": "store_delete.test_tail_moves_over_leading_only", "delete_without_confirm": "store_delete.test_delete_needs_confirm",
 "two_tries": "store_svc.test_three_tries_then_fault_open_flag_kept", "init_before_rail": "store_svc.test_rail_sequence",
 "log_drops_newest": "store_evlog.test_buffer_of_8_drops_oldest"}
btxt = []
for v, c in broken.items():
    ls = [i for i, l in enumerate(lines, 1) if l.startswith(f"{v} on ") and "as required" in l]
    if len(ls) != 2:
        raise SystemExit(f"{v}: {len(ls)} result lines")
    extra = re.search(r"cases that failed: (.*?) ;", lines[ls[0]-1]).group(1).split()
    extra = [e for e in extra if e != c]
    btxt.append(f"| `{v}` | `{c}` | l.{ls[0]} (native_sim), l.{ls[1]} (simulated chip) | {', '.join('`'+e+'`' for e in extra) if extra else 'none'} |")

up = last("UNIT ")
res = last("RESULT ")
rc = last("# remote exit code")
tw = [i for i, l in enumerate(lines, 1) if "63 of 63 executed test cases passed" in l]
tmpl = (base / "build-logs/step6/u2-notes-template.md").read_text()
k2 = ref("test_kit_disk_and_crc_names_exist")
result = sys.argv[2]
out = tmpl.replace("@@K2LINE@@", k2).replace("@@RESULT@@", result).replace("@@ROWS@@", "\n".join(rowtxt)).replace("@@BROKEN@@", "\n".join(btxt))
out = out.replace("@@CONSOLE@@", name).replace("@@UNITLINE@@", f"l.{up[0]}: `{up[1]}`").replace("@@RESLINE@@", f"l.{res[0]}: `{res[1]}`")
out = out.replace("@@RCLINE@@", f"l.{rc[0]}: `{rc[1]}`").replace("@@TWLINES@@", f"l.{tw[0]} (native_sim) and l.{tw[1]} (simulated chip)")
(base / "docs/store-notes.md").write_text(out)
print("written", len(out), "bytes; unit line", up)
