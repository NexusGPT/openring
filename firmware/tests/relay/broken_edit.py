"""Edits for tests/relay/broken_run.sh. Usage: python3 broken_edit.py <variant> <module copy folder>
Prints "<module> <named case>" for the variant. One named fault per variant; the edit must match exactly once.
module is ring_relay or ring_inbox (the copy folder holds that module)."""
import pathlib
import sys

R = "src/rrl.c"
V = {
    # a PUT is taken for finished before its last piece arrived
    "put_early": ("ring_relay", R, "test_put_not_stored_before_its_last_piece",
        "\t\tif (s->got == s->total) {",
        "\t\tif (s->got * 2 >= s->total) {"),
    # a refused (malformed) PUT still asks for a change of the store: it removes the entry of the same id
    "refused_changes_store": ("ring_relay", R, "test_refused_frames_change_nothing",
        "\t\t\t\tdrop_record(s);\n\t\t\t\trefuse(r, RRL_E_RECORD, id);\n\t\t\t\tbreak;",
        "\t\t\t\tdrop_record(s);\n\t\t\t\trefuse(r, RRL_E_RECORD, id);\n\t\t\t\tr->act = RRL_ACT_REMOVE;\n\t\t\t\tbreak;"),
    # a text is cut inside a character
    "text_cut_inside_char": ("ring_inbox", "src/rinbox.c", "test_texts_cut_at_a_character",
        "\tif (n < len) {\n\t\twhile (n > 0 && is_cont(p[n])) {\n\t\t\tn--;\n\t\t}\n\t}\n"
        "\t/* the prefix ends with an incomplete character (the sender cut it): drop that character */\n"
        "\tj = n;\n\twhile (j > 0 && back < 3 && is_cont(p[j - 1])) {\n\t\tj--;\n\t\tback++;\n\t}\n"
        "\tif (j > 0) {\n\t\tsize_t k = j - 1; /* the byte before the continuation bytes */\n\n"
        "\t\tif (seq_len(p[k]) > 1 && k + seq_len(p[k]) > n) {\n\t\t\tn = k;\n\t\t}\n\t}\n",
        "\t(void)j;\n\t(void)back;\n\t(void)seq_len;\n\t(void)is_cont;\n"),
    # REMOVE is ignored
    "remove_ignored": ("ring_relay", R, "test_remove_clear_and_hello_empty_the_store",
        "\t\t\tr->act = RRL_ACT_REMOVE;\n\t\t\tr->id = le32(&f[1]);",
        "\t\t\tr->act = RRL_ACT_NONE;\n\t\t\tr->id = le32(&f[1]);"),
    # a record of 1 byte is taken as a total
    "total_min_1": ("ring_relay", R, "test_code_4_total",
        "total < RRL_REC_MIN || total > RRL_REC_MAX", "total < 1 || total > RRL_REC_MAX"),
    # 513 is taken as a total
    "total_max_513": ("ring_relay", R, "test_code_4_total",
        "total < RRL_REC_MIN || total > RRL_REC_MAX", "total < RRL_REC_MIN || total > 513"),
    # a replace moves the entry to the front and loses its read mark
    "replace_moves_front": ("ring_inbox", "src/rinbox.c", "test_replace_keeps_place_and_read_mark",
        "\t\t(void)rinbox_modify(b, uid, category, flags);",
        "\t\tdropped_one = rinbox_add(b, uid, category, flags, dropped);"),
    # the store holds 17
    "store_17": ("ring_inbox", "include/ring_inbox/rinbox.h", "test_the_17th_pushes_the_oldest_out",
        "#define RINBOX_MAX      16", "#define RINBOX_MAX      17"),
    # a flag bit above 4 is taken as long as it is under bit 6
    "flag_bit5_ok": ("ring_relay", R, "test_code_5_malformed_record",
        "(rec[1] & ~RRL_FLAGS_MASK) != 0", "(rec[1] & ~0x3FU) != 0"),
    # code 7 is not enforced
    "code7_not_enforced": ("ring_relay", R, "test_code_7_one_source_per_link",
        "\tif (apple) {", "\tif (false) {"),
    # a repeated field type is accepted
    "repeat_type_ok": ("ring_relay", R, "test_code_5_malformed_record",
        "type < RRL_F_APP || type > RRL_F_DATE || seen[type - 1]", "type < RRL_F_APP || type > RRL_F_DATE"),
    # a category above 11 is refused
    "category_above_11_refused": ("ring_relay", R, "test_flags_and_category",
        "\tout->category = rec[0];", "\tif (rec[0] > 11) {\n\t\treturn RRL_E_RECORD;\n\t}\n\tout->category = rec[0];"),
    # the order of the pieces is not checked
    "order_ignored": ("ring_relay", R, "test_code_3_order",
        "|| id != s->id || total != s->total || off != s->got) {", "|| id != s->id || total != s->total) {"),
}
v, root = sys.argv[1], pathlib.Path(sys.argv[2])
mod, rel, case, old, new = V[v]
f = root / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print(mod, case)
