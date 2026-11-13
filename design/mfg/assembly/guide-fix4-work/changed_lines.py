#!/usr/bin/env python3
"""List, per delivered file, the line count before and after and every line number whose text changed
(before copies in before/, saved at the start of the run). Same line count and a changed-line list
means no line moved: every line citation of these files in other files still points at the same line."""
import os

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
HERE = os.path.dirname(os.path.abspath(__file__))
FILES = {
    'assembly.md': 'design/mfg/assembly/assembly.md',
    'hotbar-joint.md': 'design/mfg/assembly/hotbar-joint.md',
    'process.md': 'design/mfg/assembly/process.md',
    'joints.csv': 'design/mfg/assembly/joints.csv',
    'joint-gaps.md': 'design/mfg/assembly/joint-gaps.md',
    'board-notes.md': 'design/ecad/case/pcb/board-notes.md',
    'band-interface.md': 'design/ecad/band/band-interface.md',
    'fill_joints.py': 'design/mfg/assembly/guide-joints-work/fill_joints.py',
}
for k, rel in FILES.items():
    b = open(os.path.join(HERE, 'before', k), encoding='utf-8', newline='').read().split('\n')
    a = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read().split('\n')
    changed = [i + 1 for i in range(min(len(a), len(b))) if a[i] != b[i]]
    print(f'{rel}: lines before {len(b)} after {len(a)}; changed lines ({len(changed)}): {changed}')
