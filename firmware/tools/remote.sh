#!/bin/sh
# remote.sh: run one command for the ring firmware on the Linux build server.
#
# Usage: sh firmware/tools/remote.sh [-H] <name> "<command>"
#   <name>     a short name for the run (letters, digits, dot, dash, underscore)
#   <command>  run with bash in /ws/firmware inside the ring-os-toolchain
#              container, for example "tools/build_all.sh"
#   -H         run <command> on the server itself (not in the container), in
#              /root/ring-os/src; used for tools/setup_server.sh
#
# Optional environment:
#   RING_REMOTE_SRC  server folder for the copy (default /root/ring-os/src);
#                    must be under /root/ring-os/; used to run a test copy
#                    without touching the shared copy
#   RING_LOG_DIR     local folder for the log (default firmware/build-logs)
#
# What it does, in order:
#   1. copies firmware/ to /root/ring-os/src on the server with rsync
#      (--delete acts only inside /root/ring-os/src; build-logs/ and build
#      folders are not copied)
#   2. starts the command detached on the server at nice 19, with at most
#      8 parallel build jobs (container --cpus 8, CMAKE_BUILD_PARALLEL_LEVEL=8,
#      RING_JOBS=8), its output in /root/ring-os/logs/<id>.log
#   3. polls that log with short ssh calls and streams it here
#   4. saves it to firmware/build-logs/<date-time>-<name>.log
#   5. exits with the remote command's exit code (255 if the server could not
#      be reached for 10 minutes in a row)
#
# The ssh key stays on this Mac: it is named by path and never copied.

set -u

HOST_MODE=0
if [ "${1:-}" = "-H" ]; then
	HOST_MODE=1
	shift
fi
if [ $# -ne 2 ]; then
	echo "usage: sh firmware/tools/remote.sh [-H] <name> \"<command>\"" >&2
	exit 2
fi
NAME=$(printf '%s' "$1" | tr -c 'A-Za-z0-9._-' '_')
CMD=$2

FW_DIR=$(cd "$(dirname "$0")/.." && pwd)
SERVER="${RING_BUILD_SERVER:?set RING_BUILD_SERVER to user@host of your build server}"
KEY="${RING_BUILD_KEY:-$HOME/.ssh/<build-server-key>}"
SSH_OPTS="-i $KEY -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15"
IMAGE=ring-os-toolchain:v3.4.2
R=/root/ring-os
RSRC=${RING_REMOTE_SRC:-$R/src}
case "$RSRC" in
$R/src*) ;;
*) echo "remote.sh: RING_REMOTE_SRC must start with $R/src" >&2; exit 2 ;;
esac

STAMP=$(date +%Y%m%d-%H%M%S)
ID="$STAMP-$NAME"
LOG_DIR=${RING_LOG_DIR:-$FW_DIR/build-logs}
mkdir -p "$LOG_DIR"
LOCAL_LOG="$LOG_DIR/$ID.log"
PART="$LOG_DIR/.$ID.part"

say() {
	printf '%s\n' "$*" | tee -a "$LOCAL_LOG"
}

say "# remote.sh run $ID"
say "# command: $CMD"
say "# mode: $([ $HOST_MODE -eq 1 ] && echo host || echo container $IMAGE)"
say "# started (Mac clock): $(date '+%Y-%m-%d %H:%M:%S %Z')"

# 1. copy the source.
ssh $SSH_OPTS "$SERVER" "mkdir -p $RSRC $R/logs $R/runs $R/ws" >>"$LOCAL_LOG" 2>&1 || {
	say "# remote.sh: cannot reach the server"
	exit 255
}
# The owner's rule: stop when less than 25 GB are free on the server's /.
FREE_GB=$(ssh -n $SSH_OPTS "$SERVER" "df -BG --output=avail / | tail -1 | tr -dc 0-9" 2>>"$LOCAL_LOG")
say "# free on the server's /: ${FREE_GB:-unknown} GB"
case "$FREE_GB" in
'' | *[!0-9]*) say "# remote.sh: could not read free disk; stop"; exit 255 ;;
esac
if [ "$FREE_GB" -lt 25 ]; then
	say "# remote.sh: less than 25 GB free on the server; stop"
	exit 255
fi
rsync -a --delete \
	--exclude '/build-logs/' --exclude 'build/' --exclude '/build-*/' \
	--exclude 'twister-out*/' --exclude '.DS_Store' \
	-e "ssh $SSH_OPTS" "$FW_DIR/" "$SERVER:$RSRC/" >>"$LOCAL_LOG" 2>&1
RC=$?
if [ $RC -ne 0 ]; then
	say "# remote.sh: rsync failed with exit $RC"
	exit 255
fi
say "# source $FW_DIR copied to $RSRC"

# 2. write the run files on the server and start the run detached.
if [ $HOST_MODE -eq 1 ]; then
	RUN_LINE="cd $RSRC && nice -n 19 bash $R/runs/$ID.cmd"
else
	RUN_LINE="nice -n 19 docker run --rm --name ring-os-run-$ID --cpus 8 \
-v $R/ws:/ws -v $RSRC:/ws/firmware -v $R/runs:/runs:ro -w /ws/firmware \
-e BSIM_OUT_PATH=/ws/tools/bsim -e BSIM_COMPONENTS_PATH=/ws/tools/bsim/components \
-e CMAKE_BUILD_PARALLEL_LEVEL=8 -e RING_JOBS=8 -e RING_RUN_ID=$ID \
$IMAGE 'nice -n 19 bash /runs/$ID.cmd'"
fi

printf '%s\n' "$CMD" | ssh $SSH_OPTS "$SERVER" "cat > $R/runs/$ID.cmd" >>"$LOCAL_LOG" 2>&1
printf '#!/bin/sh\n{ %s ; } > %s/logs/%s.log 2>&1\necho $? > %s/logs/%s.exit\n' \
	"$RUN_LINE" "$R" "$ID" "$R" "$ID" |
	ssh $SSH_OPTS "$SERVER" "cat > $R/runs/$ID.wrap.sh" >>"$LOCAL_LOG" 2>&1
ssh -n $SSH_OPTS "$SERVER" \
	"touch $R/logs/$ID.log && setsid -f sh $R/runs/$ID.wrap.sh > $R/logs/$ID.wrap.log 2>&1" \
	>>"$LOCAL_LOG" 2>&1 || {
	say "# remote.sh: could not start the run"
	exit 255
}
say "# started on the server as $ID; server log $R/logs/$ID.log"

# 3. poll and stream.
OFF=0
MISSES=0
EXIT_CODE=""
while :; do
	# Read the exit file first: if it exists, the log is complete before
	# the tail below reads it.
	DONE=$(ssh -n $SSH_OPTS "$SERVER" "cat $R/logs/$ID.exit 2>&1 || true" 2>&1)
	SSH_RC=$?
	if ssh -n $SSH_OPTS "$SERVER" "tail -c +$((OFF + 1)) $R/logs/$ID.log" >"$PART" 2>&1 && [ $SSH_RC -eq 0 ]; then
		MISSES=0
		N=$(wc -c <"$PART" | tr -d ' ')
		if [ "$N" -gt 0 ]; then
			cat "$PART" | tee -a "$LOCAL_LOG"
			OFF=$((OFF + N))
		fi
		case "$DONE" in
		[0-9]*) EXIT_CODE=$DONE; break ;;
		esac
	else
		MISSES=$((MISSES + 1))
		if [ $MISSES -ge 60 ]; then
			say "# remote.sh: server unreachable for 60 polls; the run may still be going: $R/logs/$ID.log"
			exit 255
		fi
	fi
	sleep 10
done

say "# finished (Mac clock): $(date '+%Y-%m-%d %H:%M:%S %Z')"
say "# remote exit code: $EXIT_CODE"
say "# local log: $LOCAL_LOG"
exit "$EXIT_CODE"
