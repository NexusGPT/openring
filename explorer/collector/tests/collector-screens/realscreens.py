"""Builds the screen states with their pictures once per test process from the real design folder, into a temporary bundle."""
import sys
import tempfile
from pathlib import Path

EXPLORER = Path(__file__).resolve().parents[3]
ROOT = EXPLORER.parent
COLLECTOR = EXPLORER / "collector"
SOURCE = ROOT / "design" / "software" / "os" / "screens"
_cache = {}


def real():
    """{'states', 'bundle', 'manifest'}: the states as screens.py builds them, the bundle folder its pictures went to."""
    if _cache:
        return _cache
    for p in (str(COLLECTOR), str(COLLECTOR / "extract")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import run as runner  # noqa: E402
    import screens  # noqa: E402

    bundle = Path(tempfile.mkdtemp(prefix="screens-bundle-"))
    ctx = runner.Ctx("ring-model", ROOT, bundle, "0" * 40)
    states = screens.states(ctx)
    notes = []
    screens.attach_pictures(ctx, states, notes)
    _cache.update(states=states, bundle=bundle, notes=notes, manifest=(SOURCE / "manifest.md").read_text(encoding="utf-8"))
    return _cache
