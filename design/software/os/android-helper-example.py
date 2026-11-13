#!/usr/bin/env python3
"""Prints the worked example of design/software/os/android-helper-spec.md section 4.

It builds, from the tables of design/firmware.md section 7.7: the Info value, HELLO, READY, one record,
its PUT frames at a write value of 20 bytes and of 244 bytes, REMOVE, and the ACTION frame of a dismiss.
Python standard library only. Run: python3 android-helper-example.py
"""
import struct

ID = 0x000100A5
CATEGORY = 4                     # Social (section 7.6 values)
FLAGS = 0x02 | 0x10              # important (bit 1) + has a negative action (bit 4)
APP = "com.example.chat"
TITLE = "Anna"
MESSAGE = "Lunch at 12? \U0001F35C"   # ends with a 4-byte character
DATE = "20261112T191500"
LIMITS = (48, 48, 160, 15)       # application identifier, title, message, date (Info)


def hx(b):
    return " ".join("%02x" % x for x in b)


def field(t, text):
    data = text.encode("utf-8")
    assert len(data) <= 255
    return bytes([t, len(data)]) + data


def record():
    return (bytes([CATEGORY, FLAGS]) + field(1, APP) + field(2, TITLE) + field(3, MESSAGE) + field(4, DATE))


def put_frames(uid, rec, max_write):
    head = 9                      # opcode u8 + id u32 + total u16 + offset u16
    room = max_write - head
    out = []
    off = 0
    while off < len(rec):
        piece = rec[off:off + room]
        out.append((off, piece, struct.pack("<BIHH", 0x02, uid, len(rec), off) + piece))
        off += len(piece)
    return out


def main():
    print("Info (read, 6 bytes):", hx(bytes([1, 16]) + bytes(LIMITS)))
    print("HELLO  :", hx(bytes([0x01, 0x01])))
    print("READY  :", hx(bytes([0x81, 0x01, 16])))
    rec = record()
    print()
    print("id = 0x%08x, little endian: %s" % (ID, hx(struct.pack("<I", ID))))
    print("record, %d bytes:" % len(rec))
    print("  category %02x, flags %02x" % (rec[0], rec[1]))
    i = 2
    names = {1: "application identifier", 2: "title", 3: "message", 4: "date"}
    while i < len(rec):
        t, n = rec[i], rec[i + 1]
        print("  type %02x (%s), length %02x (%d), bytes %s  = %r" % (
            t, names[t], n, n, hx(rec[i + 2:i + 2 + n]), rec[i + 2:i + 2 + n].decode("utf-8")))
        i += 2 + n
    print("  whole record:", hx(rec))
    for mw in (20, 244):
        fr = put_frames(ID, rec, mw)
        print()
        print("PUT at a write value of %d bytes: %d frame(s)" % (mw, len(fr)))
        for k, (off, piece, f) in enumerate(fr, 1):
            print("  frame %d (%d bytes): 02 | %s | %s | %s | data %d bytes at offset %d" % (
                k, len(f), hx(f[1:5]), hx(f[5:7]), hx(f[7:9]), len(piece), off))
            print("    %s" % hx(f))
    print()
    print("REMOVE :", hx(struct.pack("<BI", 0x03, ID)))
    print("CLEAR  :", hx(bytes([0x04])))
    print("ACTION negative (ring to helper):", hx(struct.pack("<BIB", 0x82, ID, 1)))
    print("ACTION positive (ring to helper):", hx(struct.pack("<BIB", 0x82, ID, 0)))
    print("ERROR code 2 (no HELLO), no id   :", hx(struct.pack("<BBI", 0x83, 2, 0)))


if __name__ == "__main__":
    main()
