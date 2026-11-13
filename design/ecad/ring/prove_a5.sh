#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# A5 failure proofs: one broken copy per A5 check; the delivered files are not touched.
# Expected result written before the run: each copy exits 1 and its log holds a FAIL line with the tag in the table.
R=$REPO_ROOT/design/ecad/ring
PY=$REPO_ROOT/design/.venv/bin/python
B=$R/evidence/a5/broken
mkdir -p "$B"
cd "$R" || exit 9
"$PY" -I - > "$B/make.log" 2>&1 <<'PYEOF'
import csv
R=__import__("os").environ["REPO_ROOT"] + '/design/ecad/ring/'
rows=list(csv.DictReader(open(R+'netlist.csv')))
def save(name, f):
    rr=[dict(r) for r in rows]
    n=f(rr)
    assert n, name
    with open(R+'evidence/a5/broken/'+name,'w',newline='') as fh:
        w=csv.DictWriter(fh,list(rows[0].keys())); w.writeheader(); w.writerows(rr)
    print(name,'changed',n)
def setnet(ref,pin,net):
    def f(rr):
        n=0
        for r in rr:
            if r['reference']==ref and r['pin_number']==pin: r['net']=net; n+=1
        return n
    return f
def add_row(rr):
    rr.append(dict(net='MIC_B_CLK',reference='U7',pin_number='P1',pin_name='CLOCK',pin_type='input')); return 1
save('a5_1_u6_select_gnd.csv', setnet('U6','P5','GND'))
save('a5_2_u7_back.csv', add_row)
save('a5_3_sw4_not_ground.csv', setnet('SW4','P2','VDD_1V8'))
save('a5_4_testpad22_moved.csv', setnet('TP22','1','GND'))
save('a5_5_sw2_wrong_line.csv', setnet('SW2','P1','JOY_UP'))
save('a5_6_motor_minus_gnd.csv', setnet('M1','P2','GND'))
save('a5_7_u3_vcc_gnd.csv', setnet('U3','8','GND'))
save('a5_8_j1_p5_wrong.csv', setnet('J1','P5','VDD_3V0'))
save('a5_9_tail_ntc_gnd.csv', setnet('J_BAND_B','5','GND'))
PYEOF
: > "$B/exits.txt"
for f in a5_1_u6_select_gnd a5_2_u7_back a5_3_sw4_not_ground a5_4_testpad22_moved a5_5_sw2_wrong_line a5_6_motor_minus_gnd a5_7_u3_vcc_gnd a5_8_j1_p5_wrong a5_9_tail_ntc_gnd; do
  "$PY" -W ignore "$R/check_netlist.py" "$B/$f.csv" > "$B/check_$f.log" 2>&1
  rc=$?
  tag=$(echo "$f" | sed -E 's/^(a5_[0-9]+)_.*/\1/' | tr '_' '-' | tr a A)
  hits=$(grep -c "^FAIL $tag " "$B/check_$f.log")
  echo "$f exit $rc tag $tag FAIL-lines-with-tag $hits" >> "$B/exits.txt"
done
# A5-10: broken sheet folder: sheet file with rev A3 and the pre-A5 PDF (title block A3)
T=$B/title_a3
rm -rf "$T"; mkdir -p "$T"
cp "$R"/ring*.kicad_sch "$T/"
cp "$R/evidence/a5/ring-schematic_before.pdf" "$T/ring-schematic.pdf"
sed -i.orig 's/(rev "A5")/(rev "A3")/' "$T/ring_mics.kicad_sch"
"$PY" -W ignore "$R/check_netlist.py" "$R/netlist.csv" "$T" > "$B/check_a5_10_title_a3.log" 2>&1
rc=$?
echo "a5_10_title_a3 exit $rc tag A5-10 FAIL-lines-with-tag $(grep -c '^FAIL A5-10 ' "$B/check_a5_10_title_a3.log")" >> "$B/exits.txt"
