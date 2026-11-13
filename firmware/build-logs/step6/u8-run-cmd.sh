#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# u8-run-cmd.sh <name> <command...>: runs one command on the build server in the unit's own copy (/root/ring-os/src-u-factory).
# Output: build-logs/step6/u8-<name>.console, exit code in u8-<name>.exit.
N=$1
shift
cd $REPO_ROOT && RING_REMOTE_SRC=/root/ring-os/src-u-factory sh firmware/tools/remote.sh u8-$N "$*" > $REPO_ROOT/firmware/build-logs/step6/u8-$N.console 2>&1
echo $? > $REPO_ROOT/firmware/build-logs/step6/u8-$N.exit
