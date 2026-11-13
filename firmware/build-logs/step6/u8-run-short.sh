#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# u8-run-short.sh <n>: the suites of tests/factory alone (no broken copies) on both simulated targets, on the build server.
# Output: build-logs/step6/u8-short<n>.console, exit code in u8-short<n>.exit.
N=$1
cd $REPO_ROOT && RING_REMOTE_SRC=/root/ring-os/src-u-factory sh firmware/tools/remote.sh u8-short$N "west twister -T tests/factory -p native_sim -p nrf54lm20bsim/nrf54lm20a/cpuapp -O /ws/out/u8-short$N -j 8 --inline-logs -v" > $REPO_ROOT/firmware/build-logs/step6/u8-short$N.console 2>&1
echo $? > $REPO_ROOT/firmware/build-logs/step6/u8-short$N.exit
