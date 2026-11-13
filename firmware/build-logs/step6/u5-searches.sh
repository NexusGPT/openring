#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# u5-searches.sh: the "no" searches of unit U5 (each prints its command and every hit; an empty result is "no hit").
F=$REPO_ROOT/firmware
P=$F/modules/ring_power
echo "## 1. pure part: includes (every #include line of rpw_logic.c and rpw_logic.h)"
grep -n '#include' $P/src/rpw_logic.c $P/src/rpw_logic.h
echo "## 2. pure part: kernel or driver names in code (zephyr, k_ calls, printk, LOG_, rhw_, device, sys_, irq) in rpw_logic.c and rpw_logic.h"
grep -n -E 'zephyr|[^a-z_]k_[a-z]|printk|LOG_|rhw_|device|sys_|irq_' $P/src/rpw_logic.c $P/src/rpw_logic.h
echo "## 3. thin part: includes of rpw.c"
grep -n '#include' $P/src/rpw.c
echo "## 4. thin part: direct hardware names (i2c, gpio, regulator, sensor, DEVICE_DT, nrf_, mfd_, hal, NRF_) in rpw.c, rpw_priv.h"
grep -n -E 'i2c|gpio|regulator|sensor|DEVICE_DT|device_get|nrf_|mfd_|NRF_|npm13' $P/src/rpw.c $P/src/rpw_priv.h
echo "## 5. chip pin by number (P0.xx, P1.xx, P2.xx, pin <number>, GPIO <number>) in every file of the unit"
grep -rn -E '\bP[0-9]\.[0-9]{2}\b|[Pp]in[ _]?[0-9]+|GPIO[0-9]+' $P/src $P/CMakeLists.txt $P/Kconfig $F/tests/power/src $F/tests/power/CMakeLists.txt $F/tests/power/prj.conf $F/tests/power/testcase.yaml $F/tests/power/broken_edit.py $F/tests/power/broken_run.sh
echo "## 6. the server address, key path or user in the unit's files and notes"
grep -rn -E '46\.224|root@|<platform>-secrets|<build-server-key>|BEGIN [A-Z ]*PRIVATE' $P $F/tests/power $F/docs/power-notes.md
echo "## 7. no rail call in the unit (rail_set, rail_get) in the sources"
grep -n -E 'rail_set|rail_get' $P/src/rpw.c $P/src/rpw_logic.c $P/src/rpw_logic.h
echo "## 8. POFCONFIG or VSYSPOF in the sources (code, not comments)"
grep -n -E 'POFCONFIG|VSYSPOF' $P/src/rpw.c $P/src/rpw_logic.c $P/src/rpw_hw_real.c
echo "## 9. CHARGE_CURRENT defined where (every file of the unit)"
grep -rn -E 'define CHARGE_CURRENT|CHARGE_CURRENT' $P/src | grep -v '^.*://' | head -20
echo "## 10. numbers of the specification typed again in the sources (3450, 3300, 60000, 1000u, 96)"
grep -n -E '\b(3450|3300|60000|1000|96|150|50|20)\b' $P/src/rpw.c $P/src/rpw_logic.c $P/src/rpw_logic.h
