#!/usr/bin/env python3
"""Generate the ring core transition table from design/firmware.md section 1.2.

What is generated (exact from the document): row number, from-state, event
text, to-state. The event text is mapped to an event enum and a guard enum
by the EVENT_MAP below, keyed on the exact text of the document: a changed or
new event text stops the generator with an error, so code and document cannot
drift apart silently. The actions are prose in the document; they are
hand-written in src/state_actions.c with the row number beside each.

Usage:
  gen_table.py                 write src/state_table.inc and state_table.json
  gen_table.py --out-dir DIR   write both files into DIR (used by the fresh-run check)
  gen_table.py --doc PATH      read another copy of firmware.md
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
DEFAULT_DOC = os.path.normpath(os.path.join(MODULE, "..", "..", "..", "design", "firmware.md"))

# exact event text of section 1.2 -> (event enum suffix, guard enum suffix)
EVENT_MAP = {
    "VBUS appears (case contact)": ("VBUS_IN", "NONE"),
    "VBUS appears": ("VBUS_IN", "NONE"),
    "init done, superblock open flag clear, no VBUS, battery above B5": ("INIT_DONE", "OPEN_CLEAR_NO_VBUS_ABOVE_B5"),
    "init done, superblock open flag set": ("INIT_DONE", "OPEN_SET"),
    "init done, VBUS present": ("INIT_DONE", "VBUS"),
    "storage init fails 3 times, 200 ms apart": ("STORAGE_INIT_FAILED", "NONE"),
    "battery at B2 and no VBUS": ("BATT_B2", "NO_VBUS"),
    "battery at B5 and no VBUS": ("BATT_B5", "NO_VBUS"),
    "scan done, no VBUS": ("SCAN_DONE", "NO_VBUS"),
    "scan done, VBUS present": ("SCAN_DONE", "VBUS"),
    "read error during scan": ("SCAN_READ_ERROR", "NONE"),
    "long press of the joystick centre": ("LONG_PRESS", "NONE"),
    "long press of the joystick centre, battery at B5": ("LONG_PRESS", "AT_B5"),
    "long press of the joystick centre, free space at SFULL": ("LONG_PRESS", "SFULL"),
    "long press of the joystick centre, recording sign not drawn": ("LONG_PRESS", "SIGN_NOT_DRAWN"),
    "short press of the joystick centre": ("SHORT_PRESS", "NONE"),
    "double press of the joystick centre": ("DOUBLE_PRESS", "NONE"),
    "menu \"Power off\" confirmed": ("MENU_POWER_OFF", "NONE"),
    "battery reaches B15": ("BATT_B15", "NONE"),
    "battery reaches B5": ("BATT_B5", "NONE"),
    "battery reaches B2": ("BATT_B2", "NONE"),
    "free space at SFULL": ("STORAGE_SFULL", "NONE"),
    "BLE control \"highlight\" from a bonded phone": ("BLE_HIGHLIGHT", "NONE"),
    "VBUS appears (case insertion during a recording)": ("VBUS_IN", "NONE"),
    "free space reaches S30": ("STORAGE_S30", "NONE"),
    "chunk write fails 3 times": ("CHUNK_WRITE_FAILED", "NONE"),
    "the PDM instance gives no block for 100 ms": ("MIC_NO_BLOCK", "NONE"),
    "sudden power loss (cell cut, short, brown-out) during a write": ("POWER_LOSS", "NONE"),
    "USB configured by the case (`USBD_MSG_CONFIGURATION`)": ("USB_CONFIGURED", "NONE"),
    "VBUS removed, free space above SFULL, battery above B5": ("VBUS_OUT", "ABOVE_SFULL_ABOVE_B5"),
    "VBUS removed, free space at SFULL, battery above B5": ("VBUS_OUT", "SFULL_ABOVE_B5"),
    "VBUS removed, battery at B5": ("VBUS_OUT", "AT_B5"),
    "nPM1304 event charge error": ("CHARGE_ERROR", "NONE"),
    "long press": ("LONG_PRESS", "NONE"),
    "long press, superblock open flag set": ("LONG_PRESS", "OPEN_SET"),
    "USB suspended or unconfigured by the case": ("USB_UNCONFIGURED", "NONE"),
    "VBUS removed": ("VBUS_OUT", "NONE"),
    "command FW_END accepted": ("FW_END", "NONE"),
    "command FACTORY_ENTER with the factory flag set": ("FACTORY_ENTER", "FACTORY_FLAG"),
    "60 s elapsed": ("TIMER_60S", "NONE"),
    "storage retry succeeds, superblock open flag set": ("STORAGE_RETRY_OK", "OPEN_SET"),
    "storage retry succeeds, superblock open flag clear": ("STORAGE_RETRY_OK", "OPEN_CLEAR"),
    "storage fault set at entry (rule R-STB)": ("STORAGE_FAULT_SET", "NONE"),
    "VBUS removed, battery at B2": ("VBUS_OUT", "AT_B2"),
    "storage retry fails": ("STORAGE_RETRY_FAILED", "NONE"),
    "5 s elapsed": ("TIMER_5S", "NONE"),
    "command FACTORY_EXIT": ("FACTORY_EXIT", "NONE"),
    "command SHIP_ENTER": ("SHIP_ENTER", "NONE"),
    "command SHIP_SAMPLE (sample rings only)": ("SHIP_SAMPLE", "NONE"),
    "VBUS removed, no ship command accepted": ("VBUS_OUT", "NONE"),
}


# A guard written at the start of the actions column (F7 ruling R1, row 12, whose event text
# must stay exactly "long press of the joystick centre"): exact phrase -> guard.
# Step 6: the recording sign (rule R-SIGN, section 3.2) is part of the guard of row 12.
ACTION_GUARDS = {
    "only with the superblock open flag clear, the battery above B5, free space above SFULL and the recording sign drawn":
        "OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL_SIGN",
}


def section(text, start_pat, end_pat):
    m = re.search(start_pat, text, re.M)
    if not m:
        return None, 0
    start_line = text[: m.end()].count("\n") + 1
    rest = text[m.end():]
    e = re.search(end_pat, rest, re.M)
    return (rest[: e.start()] if e else rest), start_line


def parse_rows(doc_text):
    """Return the rows of the transition table of section 1.2 (same idea as firmware-check.py)."""
    block, start_line = section(doc_text, r"^### 1\.2 ", r"^### |^## ")
    if block is None:
        raise SystemExit("ERROR section 1.2 not found")
    rows = []
    for i, line in enumerate(block.splitlines()):
        s = line.strip()
        if not s.startswith("|") or re.match(r"^\|[\s\-|:]+\|$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "From":
            continue
        frm = re.findall(r"`([A-Z][A-Z0-9_]*)`", cells[0])
        to = re.findall(r"`([A-Z][A-Z0-9_]*)`", cells[2])
        if not (frm or to):
            continue
        if len(frm) != 1 or len(to) != 1:
            raise SystemExit(f"ERROR row needs one From and one To: {s}")
        rows.append({
            "row": len(rows) + 1,
            "doc_line": start_line + i,
            "from": frm[0],
            "event_text": cells[1],
            "to": to[0],
            "actions_text": "|".join(cells[3:]),
        })
    m = re.search(r"^The table has (\d+) transitions\.$", doc_text, re.M)
    stated = int(m.group(1)) if m else None
    return rows, stated


def fnv1a32(data):
    h = 0x811C9DC5
    for b in data:
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def canonical(rows):
    return "".join(f"{r['row']}|{r['from']}|{r['event_text']}|{r['guard']}|{r['to']}\n" for r in rows)


def c_string(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", default=DEFAULT_DOC)
    ap.add_argument("--out-dir", default=os.path.join(MODULE, "src"))
    a = ap.parse_args(argv)
    with open(a.doc, encoding="utf-8") as fh:
        text = fh.read()
    rows, stated = parse_rows(text)
    if stated is not None and stated != len(rows):
        raise SystemExit(f"ERROR the document says {stated} transitions, the table has {len(rows)}")
    for r in rows:
        if r["event_text"] not in EVENT_MAP:
            raise SystemExit(f"ERROR row {r['row']} (line {r['doc_line']}): unknown event text: {r['event_text']}")
        r["event"], r["guard"] = EVENT_MAP[r["event_text"]]
        for phrase, guard in ACTION_GUARDS.items():
            if r["actions_text"].startswith(phrase):
                if r["guard"] != "NONE":
                    raise SystemExit(f"ERROR row {r['row']}: two guards")
                r["guard"] = guard
    checksum = fnv1a32(canonical(rows).encode("utf-8"))
    os.makedirs(a.out_dir, exist_ok=True)
    inc = os.path.join(a.out_dir, "state_table.inc")
    with open(inc, "w", encoding="utf-8") as fh:
        fh.write("/* Generated by tools/gen_table.py from design/firmware.md section 1.2. Do not edit. */\n")
        fh.write(f"#define RC_TABLE_ROWS {len(rows)}\n")
        fh.write(f"#define RC_TABLE_FNV1A 0x{checksum:08x}u\n")
        for r in rows:
            fh.write(f"RC_ROW({r['row']}, {r['doc_line']}, {r['from']}, {r['event']}, {r['guard']}, {r['to']}, "
                     f"{c_string(r['event_text'])})\n")
    js = os.path.join(a.out_dir, "state_table.json")
    with open(js, "w", encoding="utf-8") as fh:
        json.dump({"source": "design/firmware.md section 1.2", "rows": len(rows),
                   "fnv1a32": f"0x{checksum:08x}", "table": rows}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"rows={len(rows)} stated={stated} fnv1a32=0x{checksum:08x} wrote {inc} {js}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
