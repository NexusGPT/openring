"""List the simulated chip (bsim) boards that tests ask for.

Usage: python3 tools/bsim_tests.py <tests folder>

Reads every testcase.yaml under the folder. A test asks for a board when the
board is in the platform_allow of one of its scenarios (or of the file's
"common" block). Prints one line per bsim board: "<board> <folder> <folder>..."
Prints nothing when no test asks for a bsim board. Exits 1 on a file it cannot
read.
"""

import pathlib
import sys

import yaml


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return value.split()
    return list(value)


def main():
    root = pathlib.Path(sys.argv[1])
    plan = {}
    for path in sorted(root.rglob("testcase.yaml")):
        try:
            data = yaml.safe_load(path.read_text()) or {}
        except (OSError, yaml.YAMLError) as err:
            print(f"cannot read {path}: {err}", file=sys.stderr)
            return 1
        common = as_list((data.get("common") or {}).get("platform_allow"))
        for scenario in (data.get("tests") or {}).values():
            boards = common + as_list((scenario or {}).get("platform_allow"))
            for board in boards:
                if board.split("/")[0].endswith("bsim"):
                    plan.setdefault(board, set()).add(str(path.parent))
    for board in sorted(plan):
        print(board, " ".join(sorted(plan[board])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
