#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"  # the repository root, found from this script
# Topic search over the files the brief lists (read-only).
R=$REPO_ROOT
F=( "$R/requirements.md" "$R/design/architecture.md" "$R/design/bom.csv" "$R/design/bom-notes.md" "$R/design/ecad/ring/sch-notes.md" "$R/design/ecad/ring/pcb/board-notes.md" "$R/design/mech/thin/thin-notes.md" "$R/design/mech/thin/placement.csv" "$R/design/mfg/mfg-notes.md" "$R/design/mfg/parts-notes.md" "$R"/design/mfg/specs/*.md "$R/design/firmware.md" "$R/design/case/case-architecture.md" "$R/design/case/case-notes.md" "$R/design/bench/bench-plan.md" "$R/design/status.json" )
for p in "$@"; do
  echo "##### $p"
  grep -n -i -E "$p" "${F[@]}" | cut -c1-260 | sed "s#$R/##"
done
