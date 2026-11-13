"""Runs the case links and the parts extractor once per test process against the real design folder (the repository this
explorer sits in). The 3D model itself is not built here: the solids are the STEP files of design/case/out/parts, named as
case.py names them."""
import sys
from pathlib import Path

EXPLORER = Path(__file__).resolve().parents[3]
ROOT = EXPLORER.parent
COLLECTOR = EXPLORER / "collector"
_cache = {}


def real():
    """{'root', 'case', 'parts', 'solids'}: the record's link fields as the extractor builds them, and the parts record."""
    if _cache:
        return _cache
    for p in (str(COLLECTOR), str(COLLECTOR / "extract")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import case  # noqa: E402
    import case_links  # noqa: E402
    import parts  # noqa: E402
    import run as runner  # noqa: E402

    ctx = runner.Ctx("case", ROOT, ROOT / "none", "0" * 40)
    solids = [f.stem for f in case.chosen_steps(ctx.source_path(case.STEP_DIR))]
    notes = []
    built = case_links.build(ctx, solids, notes)
    by_name = {x["name"]: x["part_ids"] for x in built["links"]}
    rec = {k: v for k, v in built.items() if k != "links"}
    rec["glb"] = {"nodes": [{"name": n, "part_ids": by_name[n]} for n in solids]}
    prt, _ = parts.extract(ctx)
    _cache.update({"root": ROOT, "case": rec, "parts": prt, "solids": solids, "notes": notes})
    return _cache
