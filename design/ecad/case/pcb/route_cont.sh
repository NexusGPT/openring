#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: route_cont.sh <dsn name> <ses name in> <ses name out> [passes]  continues routing from a previous session file on the server (folder /root/case-boards-route only)
H=$REPO_ROOT/design/ecad/case/pcb
D=${1:?dsn}
I=${2:?ses in}
O=${3:?ses out}
PASSES=${4:-100}
S=$H/srv.sh
$S put $H/work/$I.ses /root/case-boards-route/$I.ses || exit 2
$S ssh "cd /root/case-boards-route && rm -f $O.ses $O.run.log $O.done && (nohup sh -c 'date +\"start %F %T\" > $O.run.log; nice -n 19 docker run --rm --name case-boards-route-$O --cpus 8 -v /root/case-boards-route:/w -w /w eclipse-temurin:25-jre timeout 1500 java -jar freerouting-2.5.0.jar --gui.enabled=false -de /w/$D.dsn+/w/$I.ses -do /w/$O.ses -mp $PASSES >> $O.run.log 2>&1; echo \"exit \$?\" >> $O.run.log; date +\"end %F %T\" >> $O.run.log; touch $O.done' > $O.nohup.log 2>&1 &) ; echo started" || exit 3
for i in $(seq 1 100); do
  perl -e 'select(undef,undef,undef,10)'
  if $S ssh "test -f /root/case-boards-route/$O.done && echo yes" | grep -q yes; then break; fi
done
$S get /root/case-boards-route/$O.run.log $H/work/$O.route.log
$S get /root/case-boards-route/$O.ses $H/work/$O.ses
tail -5 $H/work/$O.route.log
