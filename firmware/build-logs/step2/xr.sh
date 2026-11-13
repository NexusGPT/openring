#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# xr.sh <label> <command> [-c]: run a command on the server for step 2.
# Default: host mode (reads the SDK on the server). With -c as third arg: in the container.
# Copy goes to /root/ring-os/src-step2; logs to build-logs/step2.
R=$REPO_ROOT
export RING_REMOTE_SRC=/root/ring-os/src-step2
export RING_LOG_DIR=$R/firmware/build-logs/step2
cd "$R" || exit 2
if [ "${3:-}" = "-c" ]; then
	exec sh firmware/tools/remote.sh "$1" "$2"
fi
exec sh firmware/tools/remote.sh -H "$1" "$2"
