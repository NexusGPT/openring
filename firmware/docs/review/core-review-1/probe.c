#include <stdio.h>
#include <string.h>
#include "ring_core/rc_core.h"
static struct rc_core c; static struct rc_actions o;
static void st(enum rc_state s){ rc_core_init(&c,RC_CENTRE_SW2,s,0); rc_actions_clear(&o);}
static void show(const char*tag){ printf("%s: state=%s row=%d acts=",tag,rc_state_name(rc_core_state(&c)),o.last_row); for(int i=0;i<o.n;i++)printf("%s ",rc_action_name(o.a[i])); printf("\n"); rc_actions_clear(&o);}
static void tickto(rc_ms_t t){ for(int i=0;i<500;i++){rc_ms_t n=rc_core_next_tick(&c); if(n>t)break; rc_core_tick(&c,n,&o);} rc_core_tick(&c,t,&o);}
int main(void){
 /* P1 press begun in CHARGING, VBUS removed at 600, long mark at 1000 */
 st(RC_ST_CHARGING); c.facts.vbus=true;
 rc_core_input(&c,RC_SW_CENTRE,true,0,&o); tickto(600); rc_core_event(&c,RC_EV_VBUS_OUT,600,&o); show("P1a vbus out at 600");
 tickto(1000); show("P1b at 1000");
 /* P2 ERR_STORAGE_FAULT first retry fails, then init ok */
 st(RC_ST_ERR_STORAGE_FAULT); tickto(60000); show("P2a 60s init fail"); c.facts.storage_init_ok=true; tickto(130000); show("P2b 130s init ok (no retry?)"); printf("next_tick=%lld\n",(long long)rc_core_next_tick(&c));
 /* P3 VBUS in BOOT */
 st(RC_ST_BOOT); rc_core_event(&c,RC_EV_VBUS_IN,1,&o); show("P3 BOOT vbus_in");
 /* P4 CHARGING vbus_out with B2 */
 st(RC_ST_CHARGING); c.facts.vbus=true; rc_core_event(&c,RC_EV_BATT_B2,1,&o); show("P4a charging B2"); rc_core_event(&c,RC_EV_VBUS_OUT,2,&o); show("P4b vbus_out at B2");
 /* P5 ERR_STORAGE_FULL then recording? long press refused */
 /* P6 BOOT init done with B5 no vbus */
 st(RC_ST_BOOT); c.facts.batt=RC_BATT_B5; rc_core_event(&c,RC_EV_INIT_DONE,1,&o); show("P6 BOOT init_done at B5");
 /* P7 batt facts never lowered: STANDBY after charge */
 st(RC_ST_STANDBY); rc_core_event(&c,RC_EV_BATT_B15,1,&o); show("P7a"); rc_core_event(&c,RC_EV_VBUS_IN,2,&o); show("P7b"); rc_core_event(&c,RC_EV_VBUS_OUT,3,&o); show("P7c vbus_out, facts.batt still B15?"); printf("batt=%d\n",c.facts.batt);
 /* P8 start recording; then long again quickly w/o release? press1 start held; in RECORDING with 2nd press at +? */
 st(RC_ST_STANDBY); rc_core_input(&c,RC_SW_CENTRE,true,0,&o); tickto(1000); show("P8a start"); rc_core_input(&c,RC_SW_CENTRE,false,1100,&o); tickto(1200); rc_core_input(&c,RC_SW_CENTRE,true,1300,&o); tickto(2300); show("P8b second long stops");
 /* P9 SW2 pressed while a dir held 10ms in STANDBY: 1000 later */
 st(RC_ST_STANDBY); rc_core_input(&c,RC_SW_UP,true,0,&o); rc_core_input(&c,RC_SW_CENTRE,true,10,&o); tickto(1010); show("P9 dir then centre 10ms later, held 1s: start");
 /* P10 highlight + STANDBY in menu with screen on: B2 reading */
 /* P11 rows 17 after VBUS cycle second B15 */
 st(RC_ST_STANDBY); rc_core_event(&c,RC_EV_BATT_B15,1,&o); show("P11a"); rc_core_event(&c,RC_EV_BATT_B15,2,&o); show("P11b second B15 in STANDBY");
 /* P12 unknown event */
 st(RC_ST_STANDBY); rc_core_event(&c,(enum rc_event)200,1,&o); show("P12 bad event");
 /* P13 B2 in STANDBY while batt fact already B2? and storage_full persists after ... */
 /* P14 CHARGING long press refused while VBUS: and thumb held through VBUS_OUT then release */
 return 0;}
