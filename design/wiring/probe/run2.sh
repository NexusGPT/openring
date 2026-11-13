#!/bin/bash
# runs on the server. usage: run2.sh <dsn> <name> ; one pass, optimizer off
cd /root/ring-wiring-probe || exit 1
D=$1; N=$2
date '+start %F %T' > $N.run.log
nice -n 19 docker run --rm --name ring-wiring-probe-$N --cpus 8 -v /root/ring-wiring-probe:/w -w /w eclipse-temurin:25-jre \
  timeout 1200 java -jar freerouting-2.5.0.jar --gui.enabled=false -de /w/$D -do /w/$N.ses -mp 1 -mt 0 >> $N.run.log 2>&1
echo "exit $?" >> $N.run.log
date '+end %F %T' >> $N.run.log
