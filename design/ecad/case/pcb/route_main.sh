#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: route_main.sh <name> [passes]   routes work/<name>.dsn on the build server with Freerouting 2.5.0 (folder /root/case-boards-route only),
# brings work/<name>.ses and work/<name>.route.log back.  Needs work/<name>.dsn.  Runs the router detached and waits for its exit line.
H=$REPO_ROOT/design/ecad/case/pcb
N=${1:?name}
PASSES=${2:-100}
S=$H/srv.sh
$S put $H/work/$N.dsn /root/case-boards-route/$N.dsn || exit 2
$S ssh "cd /root/case-boards-route && rm -f $N.ses $N.run.log $N.done && (nohup sh -c 'date +\"start %F %T\" > $N.run.log; nice -n 19 docker run --rm --name case-boards-route-$N --cpus 8 -v /root/case-boards-route:/w -w /w eclipse-temurin:25-jre timeout 1500 java -jar freerouting-2.5.0.jar --gui.enabled=false -de /w/$N.dsn -do /w/$N.ses -mp $PASSES >> $N.run.log 2>&1; echo \"exit \$?\" >> $N.run.log; date +\"end %F %T\" >> $N.run.log; touch $N.done' > $N.nohup.log 2>&1 &) ; echo started" || exit 3
for i in $(seq 1 60); do
  perl -e 'select(undef,undef,undef,10)'
  if $S ssh "test -f /root/case-boards-route/$N.done && echo yes" | grep -q yes; then break; fi
done
$S get /root/case-boards-route/$N.run.log $H/work/$N.route.log
$S get /root/case-boards-route/$N.ses $H/work/$N.ses
tail -5 $H/work/$N.route.log
