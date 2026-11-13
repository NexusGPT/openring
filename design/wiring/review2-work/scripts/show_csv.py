import csv,sys
rows=list(csv.DictReader(open(sys.argv[1])))
print("rows",len(rows))
for i,r in enumerate(rows,start=2):
    cuts=[r['cut_mm_us%d'%s] for s in range(7,14)]
    print(f"L{i} {r['id']} {r['carrier_kind']} | A {r['signal_A']} {r['end_A_board']}:{r['end_A_ref']}:{r['end_A_pin']} [{r['end_A_face']}] join={r['join_A']} | B {r['signal_B']} {r['end_B_board']}:{r['end_B_ref']}:{r['end_B_pin']} [{r['end_B_face']}] join={r['join_B']} | pair={r['pairing_rule']} | cuts={cuts} note={r['cut_note'][:80]} | mark={r['carrier_marking'][:80]} | first={r['solder_first'][:80]} | state={r['state']}")
