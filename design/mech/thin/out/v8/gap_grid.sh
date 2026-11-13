#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
T=$REPO_ROOT/design/mech/thin/out/v8
EXT=$REPO_ROOT/design/look/s1/out
PY=$REPO_ROOT/design/.venv/bin/python
cd $T || exit 9
for N in 7 8 9 10 11 12 13; do
  B=$(awk -F, -v n=$N '$1==n{print $2}' $EXT/sizes.csv)
  for MX in 0.7 0.8 0.9 1.0; do
    THIN_OVERRIDE="bore_d=$B,motor_x=$MX" nice -n 19 $PY gap_probe.py
  done
done > $T/gap_probe_grid.log 2>&1
