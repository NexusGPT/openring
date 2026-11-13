import os,sys,shutil,subprocess,re,json
R=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/firmware")
D=R+'/docs/review/core-review-4'
SRC=R+'/modules/ring_core'
M=[
('v01_r16_block_removed','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (0 && ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v02_r16_fires_at_b5_too','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && c->facts.batt >= RC_BATT_B5 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v03_r16_no_row_check','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    1) {'),
('v04_r16_only_storage_fault_state','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && from == RC_ST_ERR_STORAGE_FAULT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v05_vbus_fact_not_cleared','src/core.c','\tcase RC_EV_VBUS_OUT:\n\t\tc->facts.vbus = false;\n\t\tbreak;\n','\tcase RC_EV_VBUS_OUT:\n\t\tbreak;\n'),
('v06_r16_only_with_open_flag_clear','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && !c->facts.open_flag && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v07_r16_also_on_vbus_in','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if ((ev == RC_EV_VBUS_OUT || ev == RC_EV_VBUS_IN) && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v08_r16_skips_error_charger','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && from != RC_ST_ERR_CHARGER && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v09_r16_skips_boot','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && from != RC_ST_BOOT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v10_r16_skips_recording','src/core.c','if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {','if (ev == RC_EV_VBUS_OUT && from != RC_ST_RECORDING && c->facts.batt == RC_BATT_B2 &&\n\t    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {'),
('v11_c10_fault_set_injectable_r21','src/core.c','ev == RC_EV_BATT_B5 || ev == RC_EV_BATT_B2 || ev == RC_EV_STORAGE_FAULT_SET ||','ev == RC_EV_BATT_B5 || ev == RC_EV_BATT_B2 ||'),
('v12_c10_timer60_injectable','src/core.c','ev == RC_EV_TIMER_5S || ev == RC_EV_TIMER_60S ||','ev == RC_EV_TIMER_5S ||'),
('v13_r16_b2_event_when_state_has_row_but_vbus_stays_set_r15_entry_off','src/core.c','if (c->sm.state != from && c->facts.batt == RC_BATT_B2 && !c->facts.vbus &&','if (c->sm.state != from && c->facts.batt == RC_BATT_B2 &&'),
]
M=[m for m in M if m[1]!='src/core.h-dummy']
only=sys.argv[1:] 
os.makedirs(D+'/mut',exist_ok=True)
res=[]
for name,f,old,new in M:
    if only and name not in only: continue
    w=D+'/mut/'+name
    if os.path.exists(w+'/ring_core'): print('exists, skipping copy',name)
    else:
        os.makedirs(w,exist_ok=True)
        shutil.copytree(SRC,w+'/ring_core',ignore=shutil.ignore_patterns('__pycache__'))
        p=w+'/ring_core/'+f
        s=open(p).read()
        n=s.count(old)
        if n!=1: print('BAD PATTERN',name,n); continue
        open(p,'w').write(s.replace(old,new))
        open(w+'/mutation.diff','w').write(f'file {f}\n--- old\n{old}\n+++ new\n{new}\n')
    env=dict(os.environ,HOST_BUILD_DIR=w+'/build')
    r=subprocess.run(['nice','-n','19','sh',R+'/tests/core/host/run_host_tests.sh',w+'/ring_core'],capture_output=True,text=True,env=env)
    open(w+'/host-run.log','w').write(r.stdout+r.stderr+'exit %d\n'%r.returncode)
    fails=[l for l in r.stdout.split('\n') if l.startswith('FAIL')]
    last=[l for l in r.stdout.strip().split('\n') if l][-1] if r.stdout.strip() else ''
    # probes
    pr={}
    for pn,args in (('pA_standby_entry',[]),('pB_hold',[]),('pC_scen',[]),('pD_fuzz',['1','1500','400']),('pG_delta',[])):
        out=w+'/'+pn+'.bin'
        b=subprocess.run(['nice','-n','19',D+'/probes/build.sh',D+'/probes/'+pn+'.c',out,w+'/ring_core'],capture_output=True,text=True)
        if b.returncode: pr[pn]='build error'; continue
        q=subprocess.run(['nice','-n','19',out]+args,capture_output=True,text=True,timeout=300)
        open(w+'/'+pn+'.log','w').write(q.stdout+q.stderr+'exit %d\n'%q.returncode)
        pr[pn]=('caught' if q.returncode else 'passed')+' (exit %d)'%q.returncode
    res.append((name,len(fails),last,pr))
    print(name,'host_fail',len(fails),'|',last,'|',pr,flush=True)
json.dump(res,open(D+'/mut/results-r4.json','w'),indent=1)
