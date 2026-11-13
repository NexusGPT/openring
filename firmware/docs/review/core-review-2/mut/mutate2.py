import os,sys,shutil,subprocess,re,json
R=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/firmware")
D=R+'/docs/review/core-review-2'
SRC=R+'/modules/ring_core'
M=[
('m26b_charge_on_r8_never_added','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON) && 0) {'),
('m27b_charge_on_always_added_duplicate','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (ev == RC_EV_VBUS_IN && (has_from(out, first, RC_ACT_CHARGE_ON) || 1)) {'),
('m05b_rstb_no_storage_check','src/core.c','\t\t} else if (c->facts.storage_full) {\n\t\t\tstep(c, RC_EV_STORAGE_SFULL, t, out);\n\t\t}','\t\t}'),
('m45_row3_battery_guard_dropped_F1','src/state_table.c','return !f->open_flag && !f->vbus && f->batt < RC_BATT_B5;','return !f->open_flag && !f->vbus;'),
('m46_b15_flag_not_rearmed_by_vbus_F4','src/core.c','\t\tc->sm.b15_warned = false;   /* a new discharge starts after a charge (reading U4, ruled by C3) */\n',''),
('m47_s30_flag_not_rearmed_F4','src/state_actions.c','\t\tsm->s30_warned = false;\n',''),
('m48_timers_injectable_F4','src/core.c','ev == RC_EV_TIMER_5S || ev == RC_EV_TIMER_60S || ',''),
('m49_dir_window_4000_F7','include/ring_core/rc_gesture.h','#define RC_DIR_WINDOW_MS      40 ','#define RC_DIR_WINDOW_MS      4000 '),
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
    for pn,args in (('pA_standby_entry',[]),('pB_hold',[]),('pC_scen',[]),('pD_fuzz',['1','1500','400'])):
        out=w+'/'+pn+'.bin'
        b=subprocess.run(['nice','-n','19',D+'/probes/build.sh',D+'/probes/'+pn+'.c',out,w+'/ring_core'],capture_output=True,text=True)
        if b.returncode: pr[pn]='build error'; continue
        q=subprocess.run(['nice','-n','19',out]+args,capture_output=True,text=True,timeout=300)
        open(w+'/'+pn+'.log','w').write(q.stdout+q.stderr+'exit %d\n'%q.returncode)
        pr[pn]=('caught' if q.returncode else 'passed')+' (exit %d)'%q.returncode
    res.append((name,len(fails),last,pr))
    print(name,'host_fail',len(fails),'|',last,'|',pr,flush=True)
json.dump(res,open(D+'/mut/results-extra.json','w'),indent=1)
