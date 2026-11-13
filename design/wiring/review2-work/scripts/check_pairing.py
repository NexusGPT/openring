# pairing across the contact: ring-case-contact.csv rows against product-wiring.csv W054-W057, flex2 pad nets and case_pins pad nets
import csv
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/"); W=R+'design/wiring/review2-work/'
rows=list(csv.DictReader(open(R+'design/wiring/ring-case-contact.csv')))
pw={(r['end_A_ref'],r['end_B_ref']):(r['signal_A'],r['signal_B']) for r in csv.DictReader(open(R+'design/wiring/product-wiring.csv')) if r['carrier_kind']=='spring pin'}
cp={r['ref']:r['net'] for r in csv.DictReader(open(W+'pads/case_pins.csv'))}
bad=0
for r in rows:
    s=int(r['ring_size'].split()[1]); fl={x['ref']:x['net'] for x in csv.DictReader(open(W+'pads/flex2-us%d.csv'%s))}
    ok=pw.get((r['ring_pad'],r['case_pin']))==(r['ring_net'],r['case_net']) and fl[r['ring_pad']]==r['ring_net'] and cp[r['case_pin']]==r['case_net'] and float(r['tip_to_pad_mm'])<=0.1
    bad+=not ok
print('rows',len(rows),'sizes',len({r['ring_size'] for r in rows}))
print('RESULT pairing fails=%d of %d'%(bad,len(rows)))
