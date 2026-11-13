import os,sys,shutil,subprocess,re,json
R=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/firmware")
D=R+'/docs/review/core-review-2'
SRC=R+'/modules/ring_core'
M=[
('m01_row12_no_battery_guard','src/state_table.c','return !f->open_flag && f->batt < RC_BATT_B5 && !f->storage_full;','return !f->open_flag && !f->storage_full;'),
('m02_row12_no_storage_guard','src/state_table.c','return !f->open_flag && f->batt < RC_BATT_B5 && !f->storage_full;','return !f->open_flag && f->batt < RC_BATT_B5;'),
('m03_row12_no_openflag_guard','src/state_table.c','return !f->open_flag && f->batt < RC_BATT_B5 && !f->storage_full;','return f->batt < RC_BATT_B5 && !f->storage_full;'),
('m04_row12_b5_allowed','src/state_table.c','return !f->open_flag && f->batt < RC_BATT_B5 && !f->storage_full;','return !f->open_flag && f->batt <= RC_BATT_B5 && !f->storage_full;'),
('m05_rstb_no_storage_check','src/core.c','\t} else if (c->facts.storage_full) {\n\t\tstep(c, RC_EV_STORAGE_SFULL, t, out);\n\t}','\t}'),
('m06_rstb_storage_before_battery','src/core.c','\t\tif (c->facts.batt == RC_BATT_B2) {\n\t\t\tstep(c, RC_EV_BATT_B2, t, out);\n\t\t} else if (c->facts.batt >= RC_BATT_B5) {\n\t\t\tstep(c, RC_EV_BATT_B5, t, out);\n\t\t} else if (c->facts.storage_full) {\n\t\t\tstep(c, RC_EV_STORAGE_SFULL, t, out);\n\t\t}','\t\tif (c->facts.storage_full) {\n\t\t\tstep(c, RC_EV_STORAGE_SFULL, t, out);\n\t\t} else if (c->facts.batt == RC_BATT_B2) {\n\t\t\tstep(c, RC_EV_BATT_B2, t, out);\n\t\t} else if (c->facts.batt >= RC_BATT_B5) {\n\t\t\tstep(c, RC_EV_BATT_B5, t, out);\n\t\t}'),
('m07_rstb_b5_not_checked','src/core.c','} else if (c->facts.batt >= RC_BATT_B5) {\n\t\t\tstep(c, RC_EV_BATT_B5, t, out);\n\t\t} else if (c->facts.storage_full)','} else if (c->facts.storage_full)'),
('m08_rstb_skips_mic_fault_entry','src/core.c','if (c->sm.state == RC_ST_STANDBY && from != RC_ST_STANDBY) {','if (c->sm.state == RC_ST_STANDBY && from != RC_ST_STANDBY && from != RC_ST_ERR_MIC_FAULT) {'),
('m09_rstb_skips_transfer_entry','src/core.c','if (c->sm.state == RC_ST_STANDBY && from != RC_ST_STANDBY) {','if (c->sm.state == RC_ST_STANDBY && from != RC_ST_STANDBY && from != RC_ST_TRANSFER) {'),
('m10_rstb_b2_not_checked','src/core.c','\t\tif (c->facts.batt == RC_BATT_B2) {\n\t\t\tstep(c, RC_EV_BATT_B2, t, out);\n\t\t} else if (c->facts.batt >= RC_BATT_B5) {\n\t\t\tstep(c, RC_EV_BATT_B5, t, out);\n\t\t} else if (c->facts.storage_full) {','\t\tif (c->facts.batt >= RC_BATT_B5) {\n\t\t\tstep(c, RC_EV_BATT_B5, t, out);\n\t\t} else if (c->facts.storage_full) {'),
('m11_no_hold_cancel','src/core.c','\t\trc_gesture_cancel_hold(&c->g);  /* ruling R7: any change of state cancels a centre hold */\n',''),
('m12_hold_cancel_not_into_standby','src/core.c','\t\trc_gesture_cancel_hold(&c->g);  /* ruling R7: any change of state cancels a centre hold */','\t\tif (c->sm.state != RC_ST_STANDBY) rc_gesture_cancel_hold(&c->g);'),
('m13_hold_cancel_flag_unused','src/gesture.c','CONSIDER(g->pressing && !g->cancelled && !g->long_fired && mark_live(g, g->down_t + RC_LONG_MS),','CONSIDER(g->pressing && !g->long_fired && mark_live(g, g->down_t + RC_LONG_MS),'),
('m14_hold_cancel_not_warn','src/gesture.c','CONSIDER(g->pressing && !g->cancelled && !g->warned && !g->long_fired && mark_live(g, g->down_t + RC_WARN_MS),','CONSIDER(g->pressing && !g->warned && !g->long_fired && mark_live(g, g->down_t + RC_WARN_MS),'),
('m15_retry_one_shot','src/core.c','c->timer_next = when + RC_STORAGE_RETRY_MS;  /* ruling R3: every 60 s */','c->timer_next = RC_NO_TICK;'),
('m16_retry_period_30s','src/core.c','c->timer_next = when + RC_STORAGE_RETRY_MS;  /* ruling R3: every 60 s */','c->timer_next = when + 30000;'),
('m17_retry_never_armed','src/core.c','\t\treturn t + RC_STORAGE_RETRY_MS;','\t\treturn RC_NO_TICK;'),
('m18_retry_first_at_59s','src/core.h-dummy','',''),
('m19_open_not_set_by_OPEN','src/core.c','\t\tif (out->a[i] == RC_ACT_OPEN) {\n\t\t\tc->facts.open_flag = true;\n\t\t} else if','\t\tif (0) {\n\t\t\tc->facts.open_flag = true;\n\t\t} else if'),
('m20_open_not_cleared_by_CLOSE','src/core.c','if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_CLEAR_OPEN_FLAG ||\n\t\t\t   out->a[i] == RC_ACT_RUN_RECOVERY) {','if (out->a[i] == RC_ACT_CLEAR_OPEN_FLAG ||\n\t\t\t   out->a[i] == RC_ACT_RUN_RECOVERY) {'),
('m21_open_not_cleared_by_RUN_RECOVERY','src/core.c','if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_CLEAR_OPEN_FLAG ||\n\t\t\t   out->a[i] == RC_ACT_RUN_RECOVERY) {','if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_CLEAR_OPEN_FLAG) {'),
('m22_open_not_cleared_by_CLEAR_OPEN_FLAG','src/core.c','if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_CLEAR_OPEN_FLAG ||\n\t\t\t   out->a[i] == RC_ACT_RUN_RECOVERY) {','if (out->a[i] == RC_ACT_CLOSE ||\n\t\t\t   out->a[i] == RC_ACT_RUN_RECOVERY) {'),
('m23_initdone_b5_before_recovery','src/core.c','} else if (!c->facts.open_flag && c->facts.batt >= RC_BATT_B5) {','} else if (c->facts.batt >= RC_BATT_B5) {'),
('m24_initdone_b2_needs_open_clear','src/core.c','if (c->facts.batt == RC_BATT_B2) {\n\t\t\tev = RC_EV_BATT_B2;','if (c->facts.batt == RC_BATT_B2 && !c->facts.open_flag) {\n\t\t\tev = RC_EV_BATT_B2;'),
('m25_initdone_no_battery_read','src/core.c','if (ev == RC_EV_INIT_DONE && from == RC_ST_BOOT && !c->facts.vbus) {','if (0) {'),
('m26_charge_on_r8_removed','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (0) {'),
('m27_charge_on_duplicated','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (ev == RC_EV_VBUS_IN) {'),
('m28_charge_on_not_in_boot','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (ev == RC_EV_VBUS_IN && from != RC_ST_BOOT && !has_from(out, first, RC_ACT_CHARGE_ON)) {'),
('m29_charge_on_not_in_recovery','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (ev == RC_EV_VBUS_IN && from != RC_ST_RECOVERY && !has_from(out, first, RC_ACT_CHARGE_ON)) {'),
('m30_charge_on_not_in_error_states','src/core.c','if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {','if (ev == RC_EV_VBUS_IN && from != RC_ST_ERR_CHARGER && from != RC_ST_FACTORY_TEST && !has_from(out, first, RC_ACT_CHARGE_ON)) {'),
('m31_batt_repeat_event_on_equal','src/core.c','if (level > old) {','if (level >= old) {'),
('m32_batt_upward_fires','src/core.c','if (level > old) {','if (level != old) {'),
('m33_batt_fact_after_event','src/core.c','\tc->facts.batt = (uint8_t)level;\n\tif (level > old) {\n\t\t/* a downward crossing: the row of the threshold reached */\n\t\tsm_event(c, (enum rc_event)ev_of[level], t, out);\n\t}','\tif (level > old) {\n\t\t/* a downward crossing: the row of the threshold reached */\n\t\tsm_event(c, (enum rc_event)ev_of[level], t, out);\n\t}\n\tc->facts.batt = (uint8_t)level;'),
('m34_batt_fact_never_lowered_only_raised','src/core.c','c->facts.batt = (uint8_t)level;\n\tif (level > old)','if (level > old) c->facts.batt = (uint8_t)level;\n\tif (level > old)'),
('m35_batt_invalid_level_accepted','src/core.c','if ((unsigned)level > RC_BATT_B2) {\n\t\treturn;\n\t}','if ((unsigned)level > 9) {\n\t\treturn;\n\t}'),
('m36_long_press_injectable','src/core.c','if (ev == RC_EV_LONG_PRESS || ev == RC_EV_SHORT_PRESS','if (ev == RC_EV_SHORT_PRESS'),
('m37_row14_at_b5_only_exact','src/state_table.c','return f->batt >= RC_BATT_B5;\n\tcase RC_G_FACTORY_FLAG','return f->batt == RC_BATT_B5;\n\tcase RC_G_FACTORY_FLAG'),
('m38_row39_no_battery_guard','src/state_table.c','return f->storage_full && f->batt < RC_BATT_B5;','return f->storage_full;'),
('m39_row3_open_clear_dropped','src/state_table.c','return !f->open_flag && !f->vbus && f->batt < RC_BATT_B5;','return !f->vbus && f->batt < RC_BATT_B5;'),
('m40_sfull_event_not_a_fact','src/core.c','\tcase RC_EV_STORAGE_SFULL:\n\t\tc->facts.storage_full = true;\n\t\tbreak;\n',''),
('m41_cancel_clears_only_when_not_long_fired','src/gesture.c','if (g->pressing) {\n\t\tg->cancelled = true;','if (g->pressing && !g->long_fired) {\n\t\tg->cancelled = true;'),
('m42_row57_always_run_recovery','src/state_actions.c','\t\tif (f->open_flag) {\n\t\t\tP(RUN_RECOVERY);\n\t\t}','\t\tP(RUN_RECOVERY);'),
('m43_row57_never_run_recovery','src/state_actions.c','\t\tif (f->open_flag) {\n\t\t\tP(RUN_RECOVERY);\n\t\t}',''),
('m44_row12_open_before_m1_swapped','src/state_actions.c','\t\tP(OPEN);\n\t\tP(M1);','\t\tP(M1);\n\t\tP(OPEN);'),
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
json.dump(res,open(D+'/mut/results-%s.json'%('all' if not only else 'part'),'w'),indent=1)
