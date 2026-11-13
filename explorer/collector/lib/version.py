"""Design version readers. 'Version A4-draft, ...' is a document's own version; 'follows ... version A3'
is the version a document was made for. Two versions match when their base token (A4) matches: a
'-draft' suffix is the same design still being finished."""
import re

_TOKEN = r"([A-Z]{1,2}\d+(?:-[A-Za-z]+)?)"
_OWN = re.compile(r"\bVersion\s+" + _TOKEN)
_FOLLOWS = re.compile(r"\bfollows\b[\s\S]{0,200}?\bversion\s+" + _TOKEN, re.I)


def read_own(text):
    """The first 'Version X' in `text`, e.g. 'A4-draft', or None."""
    m = _OWN.search(text)
    return m.group(1) if m else None


def read_follows(text):
    """The version named after 'follows ... version', e.g. 'A3', or None."""
    m = _FOLLOWS.search(text)
    return m.group(1) if m else None


def base(version):
    """'A4-draft' -> 'A4'; None -> None."""
    return None if version is None else version.split("-")[0]


def is_stale(basis, current):
    """True when both are known and their base tokens differ. Unknown on either side is not stale."""
    if basis is None or current is None:
        return False
    return base(basis) != base(current)
