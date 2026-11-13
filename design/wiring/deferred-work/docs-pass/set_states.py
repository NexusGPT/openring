import csv, io, subprocess, sys
ROOT=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
CSV=ROOT+'design/wiring/deferred-triage.csv'
W='design/wiring/deferred-work/docs-pass/'
def line_of(f,q):
    hits=[i+1 for i,l in enumerate(open(ROOT+f,encoding='utf-8').read().split('\n')) if q in l]
    assert len(hits)>=1,(f,q); return hits[0]
def cite(f,q):
    return '%s line %d "%s"'%(f,line_of(f,q),q)
A='design/architecture.md'; AS='design/mfg/assembly/assembly.md'
S={}
S['10']='closed 2026-11-13: '+cite(AS,'Places of U11, C83, C84 on the board: set by the board file')+' and '+cite('design/ecad/ring/pcb/placement-final.csv','U11,OpenRing:X2SON-4_TLV755xxPDQN_1.0x1.0,F,0.000,4.200,0')
S['61']='closed 2026-11-13: the integer check is design/mech/antenna/audit.py run on antenna-study.md; '+cite('design/mech/antenna/CHECKLIST.md','claims checked: 408; without a match: 0')
S['122']=('closed 2026-11-13 for the parts the item names (U11, C83 to C88, SEAL1): '+cite(W+'check_assembly.log','A2 PASS all 131 bom.csv references named in a step')+'; '+cite(W+'check_assembly.log','A1 FAIL placement rows not in any step: side_slit_seal(SEAL3)')+'. The one remaining A1 name, SEAL3, is a new row of the inside model (design/mech/thin/placement.csv, being rewritten by the model helper), not this item; T1 fails only on line numbers of that file ('+cite(W+'check_assembly.log','RESULT FAIL A1, T1')+')')
S['123']='closed 2026-11-13: '+cite(AS,'FACTORY_EXIT comes first because removing VBUS in factory test mode reboots the ring, which would add 1 to the count (firmware issue H19')+' and '+cite(AS,'step 2 lists U11, C83, C84 (no motor switch, no diode)')+'. Not mine: design/firmware.md row H19 (line 1200) still says open'
S['124']=('open, design work: section 6 rows 4 and 5 are made, rows 2 and 3 of assembly.md are not. Row 2: '+cite(AS,'| 2 | `design/bom.csv` new row | none (no part for the floor slot sealant)')+' (bom.csv has no floor slot sealant row; the inside model has SEAL3 at design/mech/thin/placement.csv line 58). Row 3: '+cite('design/bom.csv','UV-cured dam frame on the liner')+' still reads "frame on the liner". The lead owns bom.csv')
S['129']=('open, design work: checked 2026-11-13, result in design/bom-notes.md: '+cite('design/bom-notes.md','Count of the 7: confirmed 4 (C73, C74, C75, C78)')+'; remainder: '+cite('design/bom-notes.md','C76 and C77, 1.0 nF each, no part number, 0201, net VSYS: NOT confirmed')+' and the C73 voltage rating (Murata sheet missing); the lead rules; bom.csv is not changed')
S['158']='closed 2026-11-13: '+cite(A,'(note: REPLACED by section 17.11 (record button removed; one control, the joystick); a long press of its centre records)')+'; '+cite(A,'> REPLACED by section 17.11 (record button removed; one control, the joystick): the heading')+'; '+cite(A,'record switch on the +Y edge at X -5 (REPLACED by section 17.11')+'; '+cite(A,'to reach the record switch and the joystick (REPLACED by section 17.11')+'; the other record button lines (lines 49, 154, 230, 301, 357, 371, 435, 457 and 484 hold "REPLACED by section 17.11"; the search is saved in arch-search.log) carry the mark already'
S['161']=('closed 2026-11-13: '+cite('design/supplier-package/READ-FIRST.template.html','draft: routed, passes its rules check, not built or tested')+'; '+cite('design/supplier-package/READ-FIRST.template.html','the board is routed and passes its rules check (0 violations, 0 unconnected items)')+'; '+cite('design/supplier-package/READ-FIRST.template.html','the antenna is soldered on the board at its hand end corner')+'; '+cite('design/supplier-package/make_one_pager.py','as an option the software (the circuit board is already routed)')+'; '+cite('design/supplier-package/make_one_pager.py','可选的软件开发（电路板已完成布线）')+'; source of the facts: '+cite('design/ecad/ring/pcb/board-notes-r4.md','Found 0 violations'))
b=open(CSV,'rb').read()
rows=list(csv.reader(io.StringIO(b.decode('utf-8'),newline='')))
for r in rows[1:]:
    if r[0] in S: r[5]=S[r[0]]
o=io.StringIO(newline=''); csv.writer(o,lineterminator='\r\n').writerows(rows)
open(CSV,'wb').write(o.getvalue().encode('utf-8'))
for k,v in S.items(): print(k,len(v))
