#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# usage: run.sh <name> [args...]   builds <name>.c to <name> with the real module, runs it, logs to <name>.log with the exit code
D=$REPO_ROOT/firmware/docs/review/core-review-2/probes
N=$1; shift
python3 -c "
p='$D/$N.c'
s=open(p).read().replace(' if (S() != RC_ST_RECORDING && c_mic_check(0)) {}','')
open(p,'w').write(s)"
"$D/build.sh" "$D/$N.c" "$D/$N.bin" > "$D/$N.build.log" 2>&1 || { cat "$D/$N.build.log"; exit 2; }
"$D/$N.bin" "$@" > "$D/$N.log" 2>&1
echo "exit $?" >> "$D/$N.log"
tail -12 "$D/$N.log"
