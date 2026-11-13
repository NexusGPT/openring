#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# u8-searches.sh: the source searches of unit U8 (standing rules). Output: u8-searches.log (every hit shown; "no hit" printed when none).
cd $REPO_ROOT/firmware || exit 1
FILES="modules/ring_factory tests/factory tests/bsim/factory"
echo "== 1. chip pins by number (patterns P<port>.<n>, NRF_GPIO, gpio<port> <n>)"
grep -rn -E 'P[0-9]\.[0-9]|NRF_GPIO|<&gpio[0-9]' $FILES --include=*.c --include=*.h --include=*.sh --include=*.py --include=*.overlay --include=*.conf --include=Kconfig --include=CMakeLists.txt --include=*.yaml && echo "(hits above)" || echo "no hit"
echo "== 2. kernel calls in the pure part (rfa_logic.c, rfa_logic.h): kernel headers and k_ calls"
grep -n -E 'zephyr/kernel|k_sleep|k_mutex|k_sem|k_work|k_uptime|k_spin|printk|LOG_' modules/ring_factory/src/rfa_logic.c modules/ring_factory/src/rfa_logic.h && echo "(hits above)" || echo "no hit"
echo "== 3. includes of the pure part"
grep -n '#include' modules/ring_factory/src/rfa_logic.c modules/ring_factory/src/rfa_logic.h
echo "== 4. includes of the thin part (rfa.c): hardware only through rhw.h and other units' headers"
grep -n '#include' modules/ring_factory/src/rfa.c
echo "== 5. direct hardware or kit driver names in rfa.c (gpio, i2c, spi, pdm, nrfx, device_get, DT_)"
grep -n -i -E 'gpio|i2c|spi_|pdm|nrfx|device_get|DT_|hal_' modules/ring_factory/src/rfa.c && echo "(hits above)" || echo "no hit"
echo "== 6. other companies' names in strings of this unit (Nordic, Apple, Google, Samsung, Zephyr, Android)"
grep -rn -i -E '"[^"]*(nordic|apple|google|samsung|zephyr|android)[^"]*"' $FILES --include=*.c --include=*.h && echo "(hits above)" || echo "no hit"
echo "== 7. rail call with 'on' for the microphone in this unit's sources (one-path rule: only rec_mics_on switches VDD_MIC on)"
grep -rn 'RHW_RAIL_MIC' modules/ring_factory/src && echo "(hits above)" || echo "no hit"
echo "== 8. names that start or stop a recording (rglue_input, rc_core_input, RC_EV_LONG_PRESS) in ring_factory"
grep -rn -E 'rglue_input|rc_core_input|RC_EV_LONG_PRESS' modules/ring_factory && echo "(hits above)" || echo "no hit"
echo "== 9. server address or key text in the files of this unit and in my logs (the address is read from tools/remote.sh at run time, never written here)"
ADDR=$(grep -o 'root@[0-9.]*' tools/remote.sh | head -1 | sed 's/root@//')
if [ -z "$ADDR" ]; then echo "address not found in tools/remote.sh: search not made"; else
echo "files naming the address (count): $(grep -rlF "$ADDR" $FILES docs/factory-notes.md build-logs/step6/u8-* 2>&1 | grep -c .)"; fi
grep -rn -i -E 'BEGIN .*PRIVATE|<platform>-secrets' $FILES docs/factory-notes.md && echo "(key text hits above)" || echo "no key text hit"
