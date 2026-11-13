#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# usage: run_draw.sh <tag>
R=$REPO_ROOT
W=$R/design/wiring/text-pass-work
date > $W/draw_$1.start
cd $R && nice -n 19 $R/design/.venv/bin/python $R/design/mfg/tools/draw.py > $W/draw_$1.log 2>&1
echo "exit $?" >> $W/draw_$1.log
date > $W/draw_$1.done
