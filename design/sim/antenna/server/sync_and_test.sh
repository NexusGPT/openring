#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: sync_and_test.sh <python file relative to /work> ; syncs src, tests, results dir to the server and runs one script in a throwaway container, niced
B=$REPO_ROOT/design/sim/antenna
P=$REPO_ROOT/design/wiring/probe/srv.sh
$P ssh 'mkdir -p /root/ring-antenna-sim/src /root/ring-antenna-sim/tests /root/ring-antenna-sim/results /root/ring-antenna-sim/logs' || exit 1
$P put $B/src/ /root/ring-antenna-sim/src/ || exit 1
$P put $B/tests/ /root/ring-antenna-sim/tests/ || exit 1
$P ssh "docker run --rm --name ring-antenna-test -v /root/ring-antenna-sim:/work ring-antenna-openems:1 nice -n 19 python3 -I /work/$1"
echo "exit code: $?"
$P get /root/ring-antenna-sim/results/ $B/results/
