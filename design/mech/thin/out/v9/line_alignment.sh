#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# diff operations of each edited page against its copy as found (out/v9/before/docs): only "c" (changed in place) and "a" after the last line keep the cited line numbers
D=$REPO_ROOT/design
for f in mfg/specs/body.md mfg/specs/band-liner.md mfg/specs/joystick-nub.md mfg/specs/main-board.md mfg/assembly/assembly.md architecture.md; do
  b=$D/mech/thin/out/v9/before/docs/$(basename $f)
  echo "== $f (before $(wc -l < $b) lines, now $(wc -l < $D/$f) lines)"
  diff $b $D/$f | grep -E "^[0-9]"
done
