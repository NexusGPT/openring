import csv,sys
rows=list(csv.DictReader(open(sys.argv[1])))
print("rows",len(rows))
for r in rows:
    cuts=[r['cut_mm_us%d'%s] for s in range(7,14)]
    print("|".join([r['id'],r['joint'],r['carrier_kind'],r['end_A_board'],r['end_A_ref'],r['end_A_pin'],r['end_A_face'],r['join_A'][:60],r['end_B_board'],r['end_B_ref'],r['end_B_pin'],r['end_B_face'],r['join_B'][:60],r['carrier_net'],r['carrier'][:60],"cuts="+",".join(cuts),r['cut_note'][:40],"mark="+r['carrier_marking'][:60],r['solder_first'][:80],r['state']]))
