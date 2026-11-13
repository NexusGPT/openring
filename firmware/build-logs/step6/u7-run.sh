#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# u7-run.sh <name> <remote command>: one run on the build server for unit U7 (copy of firmware/ to my own server folder).
# The console goes to build-logs/step6/u7-<name>.console, the exit code to u7-<name>.exit.
ROOT=$REPO_ROOT
NAME=$1
CMD=$2
cd "$ROOT" && RING_REMOTE_SRC=/root/ring-os/src-u-sys sh firmware/tools/remote.sh "u7-$NAME" "$CMD" > "$ROOT/firmware/build-logs/step6/u7-$NAME.console" 2>&1
echo $? > "$ROOT/firmware/build-logs/step6/u7-$NAME.exit"
