#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: poll.sh <tag> [lines]  -> tail of the log, start and end stamps
P=$REPO_ROOT/design/wiring/probe/srv.sh
$P ssh "cd /root/ring-antenna-sim/logs && cat $1.start 2>&1; tail -n ${2:-5} $1.log | cut -c1-220; cat $1.end 2>&1"
