#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: wait.sh <tag> ; waits (max ~9 min) for the end stamp file of a run, prints the log tail
P=$REPO_ROOT/design/wiring/probe/srv.sh
n=0
until $P ssh "test -f /root/ring-antenna-sim/logs/$1.end && echo yes" | grep -q yes; do perl -e 'select(undef,undef,undef,10)'; n=$((n+1)); [ $n -gt 52 ] && { echo "still running"; break; }; done
$P ssh "cd /root/ring-antenna-sim/logs && cat $1.start; tail -n ${2:-4} $1.log | cut -c1-300; cat $1.end 2>&1"
