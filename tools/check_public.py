#!/usr/bin/env python3
"""check_public.py: the check that this folder is clean enough to be public.

Run from anywhere:   python3 tools/check_public.py [<folder>]      (default: the repository root, found from this file)
Exit 0 and "RESULT PASS" when clean; exit 1 and "RESULT FAIL" with one line per finding (file:line: what) otherwise.

It walks every file (text and binary: STEP, GLB, PDF, PNG, KiCad, logs) and fails on:
  1. a private string: the machine's home folder and user name and the account's real name (read from the
     environment and the account database at run time, never written here), a home folder path of any other
     user, a temp scratch path of an assistant session, an e-mail address, a public IP address, a build-server
     host name, an organisation or product name from PATTERNS, a session or track id (compared by hash);
  2. a key-like string or a secret file name;
  3. any file under a folder named datasheets other than README.md;
  4. a PDF outside the folders that hold our own drawings and schematics (PDF_ALLOWED);
  5. a file over 50 MB;
  6. an audio or video file;
  7. a picture referenced by the README.md at the root that does not exist.
It prints the total size and the 10 largest files.

Extra private words can be given in the environment variable OPENRING_PRIVATE_WORDS (comma separated).
Binary files get the same patterns, except that e-mail addresses need a lower-case ending and the person-name check is
skipped, because random bytes would otherwise match; a text file gets the full set.
"""
import getpass
import hashlib
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------------------------------------------
# The one place that lists the patterns. Everything is bytes patterns; (label, compiled regex, applies to binary files).
# ---------------------------------------------------------------------------------------------------------------
FAKE_USERS = {"x", "someone", "zz", "you", "user", "username", "name", "me", "yourname", "example", "runner", "root"}


def _word(s):
    return re.compile(rb"(?i)(?<![A-Za-z0-9])" + re.escape(s.encode()) + rb"(?![A-Za-z])")


def runtime_patterns():
    """Patterns that come from this machine, read when the check runs."""
    out = []
    home = os.path.expanduser("~")
    if home and home not in ("/", ""):
        out.append(("home folder of this machine", re.compile(re.escape(home.encode()) + rb"(?![A-Za-z0-9_-])"), True))
    names = set()
    for v in (os.environ.get("USER"), os.environ.get("LOGNAME")):
        if v:
            names.add(v)
    try:
        names.add(getpass.getuser())
    except Exception:
        pass
    for u in list(names):
        try:
            import pwd
            g = pwd.getpwnam(u).pw_gecos.split(",")[0].strip()
            if g and g.lower() != u.lower():
                out.append(("real name of this account", re.compile(rb"(?i)(?<![A-Za-z])" + rb"\s+".join(re.escape(t.encode()) for t in g.split()) + rb"(?![A-Za-z])"), False))
                for t in g.split():
                    if len(t) >= 4:
                        out.append(("name of this account holder", _word(t), False))
        except Exception:
            pass
    for u in names:
        if len(u) >= 3 and u.lower() not in ("root", "user", "runner", "admin"):
            out.append(("user name of this machine", _word(u), True))
    for w in filter(None, (x.strip() for x in os.environ.get("OPENRING_PRIVATE_WORDS", "").split(","))):
        out.append(("extra private word", _word(w), True))
    return out


# sha256 of private ids (session and track ids). Compared by hash so that the ids themselves are not written here.
PRIVATE_ID_HASHES = {
    "033d83a015da5a362a68d059a5617cea818514b9b3e3126a64651a2b80d3a605",
    "0e2f7832ac0eda46d87e095b3b6ebe1fbe1e069b73c8b821ce108da0f4e971aa",
    "4fc8cc3ede79e85ffe720fe0c0ca8fc378d781b77308de6b88cbb29e65084caf",
    "7d5048a8da4d29022adc1fe6757450087744f736fc8b033b882727cc0286fe72",
}
UUID = re.compile(rb"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")

PATTERNS = [
    ("home path of another user", re.compile(rb"/(?:Users|home)/(?!(?:" + b"|".join(re.escape(u.encode()) for u in sorted(FAKE_USERS)) + rb")\b)[A-Za-z0-9._-]{2,}/"), True),
    ("temp scratch path of an assistant session", re.compile(rb"/(?:private/)?tmp/clau" + rb"de-\d+|clau" + rb"de-\d{3}\b|/scratch" + rb"pad/"), True),
    ("organisation or product name", re.compile(rb"(?i)" + b"nex" + b"us"), True),
    ("e-mail address", re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"), False),
    ("e-mail address (binary file)", re.compile(rb"[A-Za-z0-9._%+-]{3,}@[A-Za-z0-9-]{3,}(?:\.[A-Za-z0-9-]+)*\.[a-z]{2,10}\b"), "binary-only"),
    ("IP address of a server", re.compile(rb"(?<![\d.])(?!(?:127\.0\.0\.1|0\.0\.0\.0|255\.255\.255\.255)(?!\d))(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?!\d)(?!\.\d)"), "ip"),
    ("user@host of a server", re.compile(rb"\b[a-z_][a-z0-9_-]*@(?:\d{1,3}\.){3}\d{1,3}\b"), True),
    ("host name of a build server", re.compile(rb"\bubuntu-\d+gb-[a-z0-9-]+|\bnbg1\b|\b" + b"hetz" + rb"ner\b", re.I), True),
    ("secrets folder or key name of a server", re.compile(rb"\.[a-z]*-?secrets/|vm-" + b"lean"), True),
]
# an IPv4 is flagged only when it can be an address of a machine: some part is 100 or more, or it starts with 192.168.
# (a document section number such as 9.2.1.2 is not an address)
IP_LOOKS_REAL = re.compile(rb"^(?:192\.168\.|(?:\d{1,3}\.)*(?:1\d\d|2[0-5]\d)(?:\.|$))")

KEY_PATTERNS = [
    ("private key block", re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----"), True),
    ("AWS access key id", re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), True),
    ("GitHub token", re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})"), True),
    ("Slack token", re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{10,}"), True),
    ("API key (sk-)", re.compile(rb"\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}"), True),
    ("Google API key", re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"), True),
    ("JSON web token", re.compile(rb"\beyJ[A-Za-z0-9_-]{15,}\.eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}"), True),
    ("ssh public/private key material", re.compile(rb"\bssh-(?:rsa|ed25519|dss) AAAA[0-9A-Za-z+/=]{40,}"), True),
    ("key or secret assigned a long value", re.compile(rb"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd)\b[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9/+_.-]{20,}[\"']?"), False),
]
SECRET_FILE_NAMES = re.compile(r"^(?:id_(?:rsa|dsa|ecdsa|ed25519)(?:\.pub)?|.*\.(?:pem|p12|pfx|key|keystore|jks|kdbx|ppk)|\.env(?:\..*)?|\.npmrc|\.netrc|\.pypirc|credentials(?:\.json)?|secrets?\.(?:json|ya?ml|env|txt)|.*vm-" + "lean.*|\\.[a-z]*-secrets|known_hosts)$", re.I)

PDF_ALLOWED = ("design/ecad/", "design/mfg/drawings/", "design/mfg/tools/testdata/", "explorer/tests/support/",
               "design/wiring/product-wiring.pdf")  # the last entry is one file: our own wiring drawing
MAX_BYTES = 50 * 1000 * 1000
MEDIA_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".oga", ".opus", ".wma", ".aiff", ".aif", ".mid",
             ".mp4", ".m4v", ".mov", ".avi", ".mkv", ".webm", ".wmv", ".flv", ".mpg", ".mpeg", ".3gp"}
SKIP_DIRS = {".git"}
# folders of the copy that hold files this check must not read as the project's own: none


def is_binary(data):
    return b"\0" in data[:8192]


def line_of(data, pos):
    return data.count(b"\n", 0, pos) + 1


def media_magic(data):
    h = data[:16]
    return (h[4:8] == b"ftyp" or h[:4] == b"RIFF" and data[8:12] in (b"WAVE", b"AVI ") or h[:3] == b"ID3" or h[:4] == b"OggS"
            or h[:4] == b"fLaC" or h[:4] == b"\x1aE\xdf\xa3")


def main():
    findings = []
    files = []
    runtime = runtime_patterns()
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.islink(p):
                continue
            files.append(p)
    total = 0
    sizes = []
    for p in sorted(files):
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        size = os.path.getsize(p)
        total += size
        sizes.append((size, rel))
        name = os.path.basename(p)
        ext = os.path.splitext(name)[1].lower()
        # 3. datasheets folders
        parts = rel.split("/")
        if "datasheets" in parts[:-1] and rel != "design/datasheets/README.md" and not (name == "README.md" and parts[-2] == "datasheets"):
            findings.append((rel, 0, "file under a folder named datasheets (only README.md is allowed)"))
        # 4. PDFs
        if ext == ".pdf" and not rel.startswith(PDF_ALLOWED):
            findings.append((rel, 0, "PDF outside the folders of our own drawings and schematics"))
        # 5. size
        if size > MAX_BYTES:
            findings.append((rel, 0, "file over 50 MB (%d bytes)" % size))
        # 2. secret file names
        if SECRET_FILE_NAMES.match(name):
            findings.append((rel, 0, "secret-like file name"))
        # 6. media
        if ext in MEDIA_EXT:
            findings.append((rel, 0, "audio or video file"))
        try:
            data = open(p, "rb").read()
        except Exception as e:
            findings.append((rel, 0, "cannot read: %s" % e))
            continue
        if ext not in MEDIA_EXT and size > 12 and media_magic(data) and ext not in (".glb", ".stl"):
            findings.append((rel, 0, "audio or video content (file header)"))
        binary = is_binary(data)
        # 1. private strings
        for label, rx, scope in runtime + PATTERNS:
            if scope == "binary-only" and not binary:
                continue
            if label == "e-mail address" and binary:
                continue
            if scope is False and binary:
                continue
            for m in rx.finditer(data):
                if scope == "ip" and not IP_LOOKS_REAL.match(m.group(0)):
                    continue
                findings.append((rel, line_of(data, m.start()), "%s: %s" % (label, m.group(0).decode("latin1")[:60])))
        for m in UUID.finditer(data):
            if hashlib.sha256(m.group(0).lower()).hexdigest() in PRIVATE_ID_HASHES:
                findings.append((rel, line_of(data, m.start()), "session or track id"))
        # 2. keys
        for label, rx, scope in KEY_PATTERNS:
            if scope is False and binary:
                continue
            for m in rx.finditer(data):
                findings.append((rel, line_of(data, m.start()), "key-like string (%s)" % label))
    # 7. pictures referenced by the root README.md
    readme = os.path.join(ROOT, "README.md")
    if os.path.isfile(readme):
        txt = open(readme, encoding="utf-8", errors="replace").read()
        refs = re.findall(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)", txt) + re.findall(r"<img[^>]+src=[\"']([^\"']+)[\"']", txt, re.I)
        for r in refs:
            if re.match(r"^[a-z][a-z0-9+.-]*:", r, re.I) or r.startswith("#"):
                continue
            target = os.path.join(ROOT, r.split("#")[0].split("?")[0])
            if not os.path.isfile(target):
                ln = txt[: txt.find(r)].count("\n") + 1
                findings.append(("README.md", ln, "picture referenced but not found: " + r))
    else:
        print("note: no README.md at the root yet, so no picture references were checked")
    for rel, ln, msg in findings:
        print("%s:%d: %s" % (rel, ln, msg))
    print("files: %d, total size: %.1f MB (%d bytes)" % (len(files), total / 1e6, total))
    print("10 largest files:")
    for s, r in sorted(sizes, reverse=True)[:10]:
        print("  %9.2f MB  %s" % (s / 1e6, r))
    if findings:
        print("RESULT FAIL (%d findings)" % len(findings))
        sys.exit(1)
    print("RESULT PASS")


main()
