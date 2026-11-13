#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# Shows that check_netlist.py and the ERC can fail: broken copies only, the delivered files are not touched.
R=$REPO_ROOT/design/ecad/ring
PY=$REPO_ROOT/design/.venv/bin/python
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B=$R/evidence/broken
mkdir -p "$B"
cd "$R" || exit 9
"$PY" -I - > "$B/make.log" 2>&1 <<'EOF'
import csv
R=__import__("os").environ["REPO_ROOT"] + '/design/ecad/ring/'
rows=list(csv.DictReader(open(R+'netlist.csv')))
def save(name, rr):
    with open(R+'evidence/broken/'+name,'w',newline='') as f:
        w=csv.DictWriter(f,list(rr[0].keys())); w.writeheader(); w.writerows(rr)
a=[dict(r) for r in rows]
for r in a:
    if r['reference']=='U6' and r['pin_name']=='LR': r['net']='GND'
save('lr_swapped.csv',a)
b=[dict(r) for r in rows]
for r in b:
    if r['reference']=='U1' and r['pin_number']=='F1': r['net']='MIC_B_CLK'
save('ball_F1_moved.csv',b)
print('written')
EOF
: > "$B/exits.txt"
for f in lr_swapped ball_F1_moved; do
  "$PY" "$R/check_netlist.py" "$B/$f.csv" > "$B/check_$f.log" 2>&1
  echo "check_netlist $f exit $?" >> "$B/exits.txt"
done
# ERC probe: copy of the project without the PWR_FLAG symbols
P=$B/erc_probe
rm -rf "$P"; mkdir -p "$P"
cp "$R"/ring*.kicad_sch "$R/ring.kicad_pro" "$R/ring.kicad_sym" "$R/sym-lib-table" "$P/"
"$PY" -I - "$P/ring_power.kicad_sch" "$P/ring_main.kicad_sch" >> "$B/make.log" 2>&1 <<'EOF'
import sys
for fn in sys.argv[1:]:
    lines = open(fn).read().split('\n')
    keep = [l for l in lines if not (l.startswith('(symbol (lib_id "ring:PWR_FLAG")'))]
    print(fn, 'removed', len(lines) - len(keep))
    open(fn, 'w').write('\n'.join(keep))
EOF
"$KC" sch erc --severity-all -o "$P/erc-probe.txt" "$P/ring.kicad_sch" > "$P/erc.log" 2>&1
echo "erc probe exit $?" >> "$B/exits.txt"
grep "^\[" "$P/erc-probe.txt" | sort | uniq -c >> "$B/exits.txt"
