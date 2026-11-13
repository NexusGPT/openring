"""Runs the board and electronics extractors once per test process against the real design folder (the repository this
explorer sits in) and keeps the result for every test of collector-wiring and collector-boards."""
import atexit
import shutil
import sys
import tempfile
from pathlib import Path

EXPLORER = Path(__file__).resolve().parents[3]
ROOT = EXPLORER.parent
COLLECTOR = EXPLORER / "collector"
_cache = {}


def real():
    """{'root', 'bundle', 'electronics', 'board'}: the extractors' own output for the design as it is now."""
    if _cache:
        return _cache
    for p in (str(COLLECTOR), str(COLLECTOR / "extract")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import run as runner  # noqa: E402
    import board  # noqa: E402
    import electronics  # noqa: E402

    out = Path(tempfile.mkdtemp(prefix="explorer-wiring-test-"))
    atexit.register(shutil.rmtree, out, ignore_errors=True)
    elec, _ = electronics.extract(runner.Ctx("electronics", ROOT, out, "0" * 40))
    brd, _ = board.extract(runner.Ctx("board-files", ROOT, out, "0" * 40))
    _cache.update({"root": ROOT, "bundle": out, "electronics": elec, "board": brd})
    return _cache
