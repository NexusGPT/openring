#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: run_py.sh <tag> <limit_minutes> <ENV=VAL,ENV2=VAL2 or -> <python file under /work> args...
# Syncs src and tests, then starts ONE named container (ring-antenna-<tag>) niced and under `timeout`, in the background on the server,
# log /root/ring-antenna-sim/logs/<tag>.log. Poll with poll.sh. The container is --rm (removed when it ends).
B=$REPO_ROOT/design/sim/antenna
P=$REPO_ROOT/design/wiring/probe/srv.sh
TAG=$1; LIM=$2; ENVS=$3; shift 3
$P ssh 'mkdir -p /root/ring-antenna-sim/src /root/ring-antenna-sim/tests /root/ring-antenna-sim/results /root/ring-antenna-sim/logs /root/ring-antenna-sim/runs' || exit 1
$P put $B/src/ /root/ring-antenna-sim/src/ || exit 1
EA=""
if [ "$ENVS" != "-" ]; then IFS=, read -ra A <<< "$ENVS"; for e in "${A[@]}"; do EA="$EA -e $e"; done; fi
$P ssh "cd /root/ring-antenna-sim && rm -f logs/$TAG.end logs/$TAG.start && (nohup bash -c 'date -u +%FT%TZ > logs/$TAG.start; nice -n 19 timeout $((LIM*60)) docker run --rm --name ring-antenna-$TAG $EA -v /root/ring-antenna-sim:/work ring-antenna-openems:1 python3 -I /work/$* ; echo EXIT \$? >> logs/$TAG.log; date -u +%FT%TZ > logs/$TAG.end' > logs/$TAG.log 2>&1 &) ; sleep 1; echo started $TAG"
