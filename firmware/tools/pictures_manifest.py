#!/usr/bin/env python3
"""pictures_manifest.py <test output log> <pictures dir> <manifest out>: check the screens' pictures and write the manifest.

<test output log> is the handler.log that twister keeps for tests/screens (a passing test prints nothing into the twister log).
The script also prints the result lines of the screens suites found in it (SUITE, PASS, FAIL, SCREENS_TABLE) so the build log holds them.

The test prints one line per picture ("SCREENPIC <name> | scene: <text> | 240x120 | hash <fnv> | lit px <n> | files ..."). For each
line this script opens <dir>/<name>.png and <dir>/<name>-4x.png, checks the PNG (signature, chunk CRCs, size 240 x 120 and
960 x 480, 8-bit RGB, the deflate stream decodes to exactly the expected number of bytes) and lists the SHA-256 of both files.
Exit 0 only when every picture of the log is there and valid and there are at least MIN pictures."""
import hashlib
import pathlib
import re
import struct
import sys
import zlib

# the 21 pictures of the screens test, each exactly once (a run that loses a scene or repeats one fails)
EXPECTED = ["status", "menu", "settings", "recording-idle", "recording", "recording-highlight", "notifications-empty",
            "notifications", "notification", "modes", "control-media", "control-presenter", "control-pointer",
            "control-agent", "devices", "device", "confirm", "pairing", "charging", "message", "message-battery-low"]


def check_png(path, w, h):
    d = path.read_bytes()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return "bad signature"
    pos = 8
    ihdr = None
    idat = b""
    seen_end = False
    while pos < len(d):
        n, = struct.unpack(">I", d[pos:pos + 4])
        typ = d[pos + 4:pos + 8]
        body = d[pos + 8:pos + 8 + n]
        crc, = struct.unpack(">I", d[pos + 8 + n:pos + 12 + n])
        if zlib.crc32(typ + body) & 0xFFFFFFFF != crc:
            return "bad CRC in " + typ.decode()
        if typ == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            seen_end = True
        pos += 12 + n
    if ihdr is None or not seen_end:
        return "no IHDR or IEND"
    if ihdr[0] != w or ihdr[1] != h or ihdr[2] != 8 or ihdr[3] != 2:
        return "header says %s" % (ihdr,)
    raw = zlib.decompress(idat)
    if len(raw) != h * (1 + 3 * w):
        return "decoded %d bytes, expected %d" % (len(raw), h * (1 + 3 * w))
    return None


def main():
    log, pics, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    text = pathlib.Path(log).read_text(errors="replace").splitlines()
    for l in text:
        if any(k in l for k in ("SUITE ", " PASS - ", " FAIL - ", "SCREENS_TABLE", "SCREENPIC ", "PROJECT EXECUTION", "CROSSCHECK", "SIGNSTART", "MEMORY ")):
            print(l)
    lines = [l for l in text if "SCREENPIC " in l]
    rows = []
    bad = 0
    for l in lines:
        m = re.search(r"SCREENPIC (\S+) \| scene: (.*?) \| (\d+x\d+) \| hash (\w+) \| lit px (\d+)", l)
        if not m:
            print("unreadable picture line:", l)
            bad += 1
            continue
        name, scene, size, h, lit = m.groups()
        r = [name, scene, size, h, lit]
        for suffix, w, hh in (("", 240, 120), ("-4x", 960, 480)):
            p = pics / (name + suffix + ".png")
            if p.exists():
                # the test hook creates the file through the host's open() with no mode argument: make it readable
                p.chmod(0o644)
            if not p.exists():
                print("MISSING", p)
                bad += 1
                r += ["missing"]
                continue
            err = check_png(p, w, hh)
            if err:
                print("INVALID", p, err)
                bad += 1
            r += [hashlib.sha256(p.read_bytes()).hexdigest()[:16] + (" (invalid: %s)" % err if err else "")]
        rows.append(r)
    with out.open("w") as f:
        f.write("| picture | scene | size | frame hash (FNV-1a over the 240 x 120 RGB read-back) | lit px | sha256 of PNG (16 hex) | sha256 of 4x PNG |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| " + " | ".join(r) + " |\n")
    
    names = [r[0] for r in rows]
    for n in EXPECTED:
        if names.count(n) != 1:
            print("PICTURE %s is listed %d times, expected once" % (n, names.count(n)))
            bad += 1
    for n in names:
        if n not in EXPECTED:
            print("UNEXPECTED picture name", n)
            bad += 1
    if len(rows) != len(EXPECTED):
        print("%d picture lines, expected %d" % (len(rows), len(EXPECTED)))
        bad += 1
    print("pictures listed: %d, bad: %d, manifest %s" % (len(rows), bad, out))
    return 1 if bad else 0


sys.exit(main())
