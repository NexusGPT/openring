#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# u2-run.sh <tag> <command>: one targeted run of unit U2 on the server, console to u2-<tag>.console, exit code to u2-<tag>.exit
cd $REPO_ROOT || exit 9
date '+%Y-%m-%d %H:%M:%S' > firmware/build-logs/step6/u2-$1.start
RING_REMOTE_SRC=/root/ring-os/src-u-store sh firmware/tools/remote.sh u-store "$2" > firmware/build-logs/step6/u2-$1.console 2>&1
echo $? > firmware/build-logs/step6/u2-$1.exit
date '+%Y-%m-%d %H:%M:%S' > firmware/build-logs/step6/u2-$1.end
