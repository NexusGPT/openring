"""Edits for tests/xfer/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_xfer copy folder>
Prints two lines: the named case (suite.case) that must fail, then the cases that MAY also fail because they run the same
broken code (space separated, or "-"). One named fault per variant; the edit must match exactly once.
The variants are those of firmware/docs/step6-plan.md, unit U4 "Broken copies"."""
import pathlib
import sys

V = {
    # the response header carries tag 0 instead of the request's tag
    "tag_not_echoed": ("src/rxf_proto.c", "xfer_proto.test_tag_echoed",
        "\tput32(out + RREC_MSG_OFF_TAG, tag);\n",
        "\tput32(out + RREC_MSG_OFF_TAG, 0u);\n"),
    # a response with an empty payload carries a CRC other than 0
    "crc_on_empty": ("src/rxf_proto.c", "xfer_proto.test_crc_zero_for_empty",
        "rxf_proto_put_header(c->stage, h->opcode, st, h->tag, len, rxf_proto_payload_crc(c->stage + RREC_MSG_HEADER_BYTES, len));",
        "rxf_proto_put_header(c->stage, h->opcode, st, h->tag, len, len == 0u ? 0xFFFFFFFFu : rxf_proto_payload_crc(c->stage + RREC_MSG_HEADER_BYTES, len));"),
    # the BAD_CRC response carries a payload of 4 bytes
    "bad_crc_payload": ("src/rxf_proto.c", "xfer_proto.test_bad_crc",
        "\tlen = 0u;   /* an error response has no payload (FW l.690) */\n",
        "\tlen = st == RREC_ST_BAD_CRC ? 4u : 0u;\n"),
    # LIST_RECORDINGS accepts max 65
    "list_max_65": ("src/rxf_proto.c", "xfer_proto.test_list_args",
        "max < RREC_LIST_MAX_MIN || max > RREC_LIST_MAX_MAX) {",
        "max < RREC_LIST_MAX_MIN || max > RREC_LIST_MAX_MAX + 1u) {"),
    # READ_RANGE accepts a count of 257
    "range_257": ("src/rxf_proto.c", "xfer_proto.test_read_range_args",
        "count < RREC_READ_COUNT_MIN || count > RREC_READ_COUNT_MAX) {",
        "count < RREC_READ_COUNT_MIN || count > RREC_READ_COUNT_MAX + 1u) {"),
    # a command that arrives while another runs is not answered BUSY (it runs at once)
    "no_busy": ("src/rxf_proto.c", "xfer_proto.test_busy_while_running",
        "if (__atomic_exchange_n(&c->running, 1, __ATOMIC_ACQ_REL) != 0) {",
        "if (__atomic_exchange_n(&c->running, 1, __ATOMIC_ACQ_REL) != 0 && false) {"),
    # the protocol takes the factory command as allowed whatever the backend says
    "factory_flag_ignored": ("src/rxf_proto.c", "xfer_proto.test_factory_not_allowed",
        "\t\tst = be->factory(p, plen, out, &olen);\n",
        "\t\t(void)be->factory(p, plen, out, &olen);\n"),
    # the high-speed table carries the full-speed packet size
    "hs_packet_64": ("src/rxf_desc.c", "xfer_desc.test_descriptor_bytes_fs_hs",
        "(uint16_t)RREC_USB_MPS_HS :",
        "(uint16_t)RREC_USB_MPS_FS :"),
    # the stack is enabled when the class starts, before the power chip reported VBUS
    "usb_on_without_vbus": ("src/rxf_class.c", "xfer_svc.test_stack_follows_vbus",
        "\trhw_usb()->set_callbacks(&usb_cb);\n\treturn 0;\n",
        "\trhw_usb()->set_callbacks(&usb_cb);\n\t(void)rhw_usb()->enable();\n\treturn 0;\n"),
    # a range the store says is not there (a deleted recording) is read and sent anyway: NOT_FOUND is ignored in the
    # range check and in the reads
    "read_deleted": ("src/rxf_proto.c", "xfer_store.test_read_range_deleted_not_found",
        "\tst = c->be->range_check(rec, first, count);\n"
        "\tif (st != RREC_ST_OK) {\n"
        "\t\treturn finish_small(c, emit, user, h, st, 0u, res);\n"
        "\t}\n"
        "\t/* pass 1: the header's CRC covers the whole payload and comes before it (FW l.686, rxf.h) */\n"
        "\tfor (uint32_t i = 0; i < count; i++) {\n"
        "\t\tif (stopped(c)) {\n"
        "\t\t\treturn RXF_ABORTED;\n"
        "\t\t}\n"
        "\t\tst = c->be->read_chunk(rec, first + i, s);\n"
        "\t\tif (st != RREC_ST_OK) {\n",
        "\tst = c->be->range_check(rec, first, count);\n"
        "\tif (st != RREC_ST_OK && st != RREC_ST_NOT_FOUND) {\n"
        "\t\treturn finish_small(c, emit, user, h, st, 0u, res);\n"
        "\t}\n"
        "\t/* pass 1: the header's CRC covers the whole payload and comes before it (FW l.686, rxf.h) */\n"
        "\tfor (uint32_t i = 0; i < count; i++) {\n"
        "\t\tif (stopped(c)) {\n"
        "\t\t\treturn RXF_ABORTED;\n"
        "\t\t}\n"
        "\t\tst = c->be->read_chunk(rec, first + i, s);\n"
        "\t\tif (st != RREC_ST_OK && st != RREC_ST_NOT_FOUND) {\n"),
}

# cases that may fail in the same broken copy because they run the same broken code; anything else failing is a defect
# of the copy and fails the run (each listed with its reason in firmware/docs/xfer-notes.md)
ALSO = {
    # every case that reads the tag of a response (header bytes, errors, the transport and the store cases all compare it)
    "tag_not_echoed": [
        "xfer_proto.test_bad_crc",
        "xfer_proto.test_bad_magic",
        "xfer_proto.test_busy_while_running",
        "xfer_proto.test_confirm_delete_args",
        "xfer_proto.test_factory_not_allowed",
        "xfer_proto.test_fw_args",
        "xfer_proto.test_get_info_layout",
        "xfer_proto.test_get_log_args",
        "xfer_proto.test_header_bytes",
        "xfer_proto.test_list_args",
        "xfer_proto.test_read_range_args",
        "xfer_proto.test_read_range_failures",
        "xfer_proto.test_read_range_stream",
        "xfer_proto.test_unknown_opcodes",
        "xfer_store.test_case_digest_matches_close",
        "xfer_store.test_confirm_then_delete",
        "xfer_store.test_get_info_from_store",
        "xfer_store.test_get_log_records",
        "xfer_store.test_list_entries",
        "xfer_store.test_read_range_bytes_equal_disk",
        "xfer_store.test_read_range_deleted_not_found",
        "xfer_store.test_resume_from_any_chunk",
        "xfer_store.test_set_time_and_factory_over_usb",
        "xfer_svc.test_bad_magic_and_resync",
        "xfer_svc.test_busy_over_transport",
        "xfer_svc.test_request_in_pieces",
    ],
    # the cases that check the reference CRC or zero CRC of a response without payload (header bytes; the store cases check every response's CRC)
    "crc_on_empty": [
        "xfer_proto.test_header_bytes",
        "xfer_store.test_case_digest_matches_close",
        "xfer_store.test_confirm_then_delete",
        "xfer_store.test_read_range_bytes_equal_disk",
        "xfer_store.test_read_range_deleted_not_found",
        "xfer_store.test_set_time_and_factory_over_usb",
    ],
    "bad_crc_payload": [],
    # the store case that sends max 65 and expects BAD_ARG
    "list_max_65": [
        "xfer_store.test_list_entries",
    ],
    "range_257": [],
    "no_busy": [],
    # the store case that sends FACTORY with the flag clear and expects NOT_ALLOWED
    "factory_flag_ignored": [
        "xfer_store.test_set_time_and_factory_over_usb",
    ],
    "hs_packet_64": [],
    "usb_on_without_vbus": [],
    # the protocol case that gets NOT_FOUND from the fake's range check and expects the error
    "read_deleted": [
        "xfer_proto.test_read_range_args",
    ],
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
