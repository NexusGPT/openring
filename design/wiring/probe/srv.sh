#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# usage: srv.sh ssh "<cmd>" | srv.sh put <local> <remote> | srv.sh get <remote> <local>; output masked
RS=$REPO_ROOT/firmware/tools/remote.sh
SERVER=$(sed -n 's/^SERVER=//p' $RS)
IP=${SERVER#*@}
KEY="~/.ssh/<build-server-key>"
OPTS=(-i "$KEY" -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15)
case "$1" in
 ssh) ssh "${OPTS[@]}" "$SERVER" "$2" 2>&1 ;;
 put) rsync -a -e "ssh ${OPTS[*]}" "$2" "$SERVER:$3" 2>&1 ;;
 get) rsync -a -e "ssh ${OPTS[*]}" "$SERVER:$2" "$3" 2>&1 ;;
esac | sed "s/$IP/<build-server>/g"
exit ${PIPESTATUS[0]}
