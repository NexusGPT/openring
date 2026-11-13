import re,sys
doc=open((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/firmware.md")).read().split('\n')
rows=[l for l in doc[132:203]]  # lines 133..198
assert all(l.startswith('| ') for l in rows), 'table lines'
spec=[]
for l in rows:
    c=[x.strip() for x in l.strip().strip('|').split('|')]
    spec.append(c)
assert len(spec)==71
S=lambda s:s.replace('`','')
# expected actions typed from the specification's action column (my own reading)
A={1:'CHARGE_ON',2:'CHARGE_ON',3:'SD_OFF',4:'SD_ON',5:'SD_OFF CHARGE_ON',6:'LOG_EVENT MF',7:'SHIP_MODE',8:'SD_OFF M3',
9:'WRITE_CLOSE_RECOVERED CLEAR_OPEN_FLAG SD_OFF',10:'WRITE_CLOSE_RECOVERED CLEAR_OPEN_FLAG SD_OFF CHARGE_ON',11:'LOG_EVENT MF',
12:'OPEN M1',13:'SD_ON MOUNT',14:'SCR_MSG_BATTERY_LOW_3S',15:'SCR_MSG_STORAGE_FULL_3S',16:'SCREEN_ON SCR_STATUS_5S',17:'',
18:'SAVE_SETTINGS_TIME M2 SHIP_MODE',19:'CHARGE_ON',20:'M3 SCR_STATUS_5S',21:'M3',22:'SAVE_SETTINGS_TIME SHIP_MODE',23:'M3',24:'',
25:'CLOSE M2',26:'HIGHLIGHT MH SCR_RECORDING_3S',27:'',28:'HIGHLIGHT MH',29:'CLOSE M2 CHARGE_ON',30:'M3',31:'CLOSE M3',32:'CLOSE SHIP_MODE',
33:'M3 SCR_MSG_30MIN_3S',34:'CLOSE M3',35:'STOP_PDM CLOCKS_LOW MIC_OFF MF',36:'CLOSE MF',37:'',38:'SD_ON MOUNT',39:'',40:'',41:'SAVE_SETTINGS_TIME SHIP_MODE',42:'',
43:'LOG_CHARGE_ERROR CHARGE_OFF MF',44:'M3 SCR_MSG_IN_CASE_3S',45:'FINISH_COMMAND SD_OFF CHARGE_ON',46:'ABORT_COMMAND SD_OFF',
47:'REQUEST_UPGRADE_TEST REBOOT',48:'FACTORY_MODE',49:'M3',50:'CHARGE_ON',51:'M3 SCR_MSG_STORAGE_FULL_3S',52:'M3',53:'SHIP_MODE',
54:'CHARGE_ON',55:'M3 SCR_MSG_BATTERY_LOW_3S',56:'SAVE_SETTINGS_TIME SHIP_MODE',57:'CHARGE_ON',58:'RETRY_STORAGE',59:'SD_ON',60:'',61:'',62:'SHIP_MODE',
63:'',64:'CHARGE_ON',65:'SAVE_SETTINGS_TIME SHIP_MODE',66:'',67:'SAVE_SETTINGS_TIME SHIP_MODE',68:'REBOOT',69:'CLEAR_FACTORY_FLAG SHIP_MODE',70:'SHIP_MODE',71:'REBOOT'}
EXTRA={('16','v1'):'SCREEN_CENTRE MT'}
# guard expected from the specification's event text
G={3:'OPEN_CLEAR_NO_VBUS_ABOVE_B5',4:'OPEN_SET',5:'VBUS',7:'NO_VBUS',8:'NO_VBUS',9:'NO_VBUS',10:'VBUS',12:'OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL',13:'OPEN_SET',14:'AT_B5',15:'SFULL',39:'ABOVE_SFULL_ABOVE_B5',40:'SFULL_ABOVE_B5',41:'AT_B2',42:'AT_B5',48:'FACTORY_FLAG',59:'OPEN_SET',60:'OPEN_CLEAR'}
bad=0;n=0;seen=set()
for line in open(sys.argv[1]):
    p=line.rstrip('\n').split('|')
    row=int(p[0]);fr,ev,gd,to,got,after,acts,var=p[1:9]
    n+=1
    seen.add(row)
    sp=spec[row-1]
    exp_from=S(sp[0]); exp_ev=sp[1]; exp_to=S(sp[2])
    st={'`':''}
    errs=[]
    if fr!=exp_from: errs.append('from %s != %s'%(fr,exp_from))
    if to!=exp_to: errs.append('to %s != %s'%(to,exp_to))
    if ev!=exp_ev and ev!=S(exp_ev) and not (exp_ev.startswith(ev) or exp_ev.replace('`','').startswith(ev.replace('`',''))): errs.append('event "%s" vs "%s"'%(ev,exp_ev))
    if gd!=G.get(row,'NONE'): errs.append('guard %s != %s'%(gd,G.get(row,'NONE')))
    if got!='got=%d'%row: errs.append('handle took row %s not %d'%(got,row))
    if after!=to: errs.append('state after %s != %s'%(after,to))
    e=EXTRA.get((str(row),var),A[row])
    if acts!=e: errs.append('actions "%s" != "%s"'%(acts,e))
    if errs:
        bad+=1;print('DIFF row',row,var,errs)
print('lines checked',n,'rows seen',len(seen),'diff lines',bad)
