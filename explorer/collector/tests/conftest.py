"""Shared pytest setup for every collector test folder."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

COLLECTOR = Path(__file__).resolve().parents[1]
EXPLORER = COLLECTOR.parent
sys.path.insert(0, str(COLLECTOR))

RUN = COLLECTOR / "run.py"
SAMPLE_BUNDLE = EXPLORER / "tests" / "support" / "sample-bundle"


def run_collector(*args, cwd=None):
    """Run collector/run.py as a user would. Returns the CompletedProcess."""
    return subprocess.run([sys.executable, str(RUN), *args], capture_output=True, text=True, cwd=cwd)


@pytest.fixture
def sample_bundle():
    return SAMPLE_BUNDLE


@pytest.fixture
def source_repo(tmp_path):
    """A tiny git repo shaped like the real one: design/ plus the three root documents."""
    root = tmp_path / "repo"
    (root / "design").mkdir(parents=True)
    (root / "design" / "note.md").write_text("Version ZV1\n")
    for n in ("requirements.md", "feasibility.md", "partners.md"):
        (root / n).write_text("zz\n")
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "zz"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True, env=env, capture_output=True)
    return root


@pytest.fixture
def extractors(tmp_path):
    """Write extractor modules into a temp folder and return (folder, writer)."""
    folder = tmp_path / "extract"
    folder.mkdir()

    def write(name, body):
        (folder / f"{name}.py").write_text(body)

    return folder, write


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
