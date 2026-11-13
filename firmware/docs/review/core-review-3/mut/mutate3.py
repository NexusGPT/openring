import os,sys,shutil,subprocess,re,json
R=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/firmware")
D=R+'/docs/review/core-review-3'
SRC=R+'/modules/ring_core'
M=[
('r01_b2_entry_check_removed','src/core.c','if (c->sm.state != from && c->facts.batt == RC_BATT_B2 && !c->facts.vbus &&','if (c->sm.state != from && 0 && c->facts.batt == RC_BATT_B2 && !c->facts.vbus &&'),
('r02_b2_entry_skips_mic_fault','src/core.c','c->sm.state == RC_ST_ERR_MIC_FAULT || c->sm.state == RC_ST_ERR_CHARGER)) {','c->sm.state == RC_ST_ERR_CHARGER)) {'),
('r03_b2_entry_skips_charger','src/core.c','c->sm.state == RC_ST_ERR_MIC_FAULT || c->sm.state == RC_ST_ERR_CHARGER)) {','c->sm.state == RC_ST_ERR_MIC_FAULT)) {'),
('r04_b2_entry_ignores_vbus','src/core.c','if (c->sm.state != from && c->facts.batt == RC_BATT_B2 && !c->facts.vbus &&','if (c->sm.state != from && c->facts.batt == RC_BATT_B2 &&'),
('r05_b2_entry_skips_storage_fault_state','src/core.c','c->sm.state == RC_ST_STANDBY || c->sm.state == RC_ST_ERR_STORAGE_FAULT ||','c->sm.state == RC_ST_STANDBY ||'),
('r06_rstb_fault_check_dropped','src/core.c','\t\tif (c->facts.storage_fault) {\n\t\t\tstep(c, RC_EV_STORAGE_FAULT_SET, t, out);\n\t\t} else if (c->facts.batt >= RC_BATT_B5) {','\t\tif (c->facts.batt >= RC_BATT_B5) {'),
('r07_fault_fact_not_set_on_entry','src/core.c','\t\t\tc->facts.storage_fault = true;  /* ruling R11 */\n',''),
('r08_retry_ok_keeps_fault','src/core.c','\tcase RC_EV_INIT_DONE:\n\tcase RC_EV_STORAGE_RETRY_OK:\n','\tcase RC_EV_INIT_DONE:\n'),
('r09_init_done_keeps_fault','src/core.c','\tcase RC_EV_INIT_DONE:\n\tcase RC_EV_STORAGE_RETRY_OK:\n','\tcase RC_EV_STORAGE_RETRY_OK:\n'),
('r10_recovery_entry_clears_open_flag','src/core.c','\t\tif (c->sm.state == RC_ST_ERR_STORAGE_FAULT) {\n\t\t\tc->facts.storage_fault = true;','\t\tif (c->sm.state == RC_ST_RECOVERY) c->facts.open_flag = false;\n\t\tif (c->sm.state == RC_ST_ERR_STORAGE_FAULT) {\n\t\t\tc->facts.storage_fault = true;'),
('r11_clear_open_flag_ignored','src/core.c','if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_CLEAR_OPEN_FLAG) {','if (out->a[i] == RC_ACT_CLOSE) {'),
('r12_retry_every_missed_period','src/core.c','c->timer_next = now + RC_STORAGE_RETRY_MS;','c->timer_next = when + RC_STORAGE_RETRY_MS;'),
('r13_retry_next_in_30s','src/core.c','c->timer_next = now + RC_STORAGE_RETRY_MS;','c->timer_next = now + 30000;'),
('r14_boot_battery_applied_at_once','src/core.c','\tif (c->sm.state == RC_ST_BOOT) {\n\t\treturn;  /* ruling R12: kept; the order at "init done" decides */\n\t}\n',''),
('r15_boot_battery_level_not_kept','src/core.c','\tc->facts.batt = (uint8_t)level;\n\tif (c->sm.state == RC_ST_BOOT) {\n\t\treturn;','\tif (c->sm.state == RC_ST_BOOT) {\n\t\treturn;'),
('r16_row8_no_sd_off','src/state_actions.c','\t\tP(SD_OFF);\n\t\tP(M3);\n\t\tbreak;\n\tcase 9:','\t\tP(M3);\n\t\tbreak;\n\tcase 9:'),
('r17_row41_no_ship','src/state_actions.c','\t\tP(SAVE_SETTINGS_TIME);\n\t\tP(SHIP_MODE);\n\t\tbreak;\n\tcase 42:','\t\tP(SAVE_SETTINGS_TIME);\n\t\tbreak;\n\tcase 42:'),
('r18_row41_guard_ge_b5','src/state_table.c','return f->batt == RC_BATT_B2;','return f->batt >= RC_BATT_B5;'),
('r19_initdone_b2_needs_flag_clear','src/core.c','if (c->facts.batt == RC_BATT_B2) {\n\t\t\tev = RC_EV_BATT_B2;','if (c->facts.batt == RC_BATT_B2 && !c->facts.open_flag) {\n\t\t\tev = RC_EV_BATT_B2;'),
('r20_init_failed_b2_not_checked_via_state_set','src/core.c','c->sm.state == RC_ST_STANDBY || c->sm.state == RC_ST_ERR_STORAGE_FAULT ||','c->sm.state == RC_ST_STANDBY || c->sm.state == RC_ST_ERR_STORAGE_FAULT && from != RC_ST_BOOT ||'),
('r21_internal_fault_event_injectable','src/core.c','ev == RC_EV_BATT_B5 || ev == RC_EV_BATT_B2 || ev == RC_EV_STORAGE_FAULT_SET ||','ev == RC_EV_BATT_B5 || ev == RC_EV_BATT_B2 ||'),
('r22_row59_open_flag_guard_inverted','src/state_table.c','\tcase RC_G_OPEN_CLEAR:\n\t\treturn !f->open_flag;','\tcase RC_G_OPEN_CLEAR:\n\t\treturn true;'),
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
json.dump(res,open(D+'/mut/results-r3.json','w'),indent=1)
