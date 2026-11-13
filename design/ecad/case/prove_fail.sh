#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# Shows that check_netlist.py and the ERC can fail: broken copies only, the delivered files are not touched.
R=$REPO_ROOT/design/ecad/case
PY=$REPO_ROOT/design/.venv/bin/python
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B=$R/evidence/broken
mkdir -p "$B"
cd "$R" || exit 9
"$PY" -I - > "$B/make.log" 2>&1 <<'EOF'
import csv
R=__import__("os").environ["REPO_ROOT"] + '/design/ecad/case/'
rows=list(csv.DictReader(open(R+'netlist.csv')))
def save(name, rr):
    with open(R+'evidence/broken/'+name,'w',newline='') as f:
        w=csv.DictWriter(f,list(rr[0].keys())); w.writeheader(); w.writerows(rr)
a=[dict(r) for r in rows]
for r in a:
    if r['reference']=='P2': r['net']='USB_D+'
save('pins_P2_swapped.csv',a)
b=[dict(r) for r in rows]
for r in b:
    if r['reference']=='U1' and r['pin_number']=='19': r['net']='VRING_FAULT_N'
save('u1_pin19_moved.csv',b)
print('written')
EOF
: > "$B/exits.txt"
for f in pins_P2_swapped u1_pin19_moved; do
  "$PY" "$R/check_netlist.py" "$B/$f.csv" > "$B/check_$f.log" 2>&1
  echo "check_netlist $f exit $?" >> "$B/exits.txt"
done
# ERC probe: copy of the project without the PWR_FLAG symbols
P=$B/erc_probe
rm -rf "$P"; mkdir -p "$P"
cp "$R"/case*.kicad_sch "$R/case.kicad_pro" "$R/case.kicad_sym" "$R/sym-lib-table" "$P/"
"$PY" -I - "$P/case_power.kicad_sch" >> "$B/make.log" 2>&1 <<'EOF'
import sys
for fn in sys.argv[1:]:
    lines = open(fn).read().split('\n')
    keep = [l for l in lines if not (l.startswith('(symbol (lib_id "case:PWR_FLAG")'))]
    print(fn, 'removed', len(lines) - len(keep))
    open(fn, 'w').write('\n'.join(keep))
EOF
"$KC" sch erc --severity-all -o "$P/erc-probe.txt" "$P/case.kicad_sch" > "$P/erc.log" 2>&1
echo "erc probe exit $?" >> "$B/exits.txt"
grep "^\[" "$P/erc-probe.txt" | sort | uniq -c >> "$B/exits.txt"
