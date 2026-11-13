#include <stdio.h>
#include "ring_core/rc_core.h"
static struct rc_core c; static struct rc_actions o;
static void st(enum rc_state s){ rc_core_init(&c,RC_CENTRE_SW2,s,0); rc_actions_clear(&o);}
static void show(const char*tag){ printf("%s: state=%s row=%d acts=",tag,rc_state_name(rc_core_state(&c)),o.last_row); for(int i=0;i<o.n;i++)printf("%s ",rc_action_name(o.a[i])); printf("\n"); rc_actions_clear(&o);}
static void tickto(rc_ms_t t){ for(int i=0;i<500;i++){rc_ms_t n=rc_core_next_tick(&c); if(n>t)break; rc_core_tick(&c,n,&o);} rc_core_tick(&c,t,&o);}
int main(void){
 /* Q1: ERR_MIC_FAULT, battery reaches B5 (no row), 5 s later STANDBY, long press starts a recording at B5 */
 st(RC_ST_ERR_MIC_FAULT); rc_core_event(&c,RC_EV_BATT_B5,1,&o); show("Q1a B5 in ERR_MIC_FAULT"); tickto(5000); show("Q1b 5 s");
 rc_core_input(&c,RC_SW_CENTRE,true,6000,&o); tickto(7000); show("Q1c long press at batt=B5"); printf("batt=%d\n",c.facts.batt);
 /* Q2: TRANSFER, vbus out with storage full */
 st(RC_ST_TRANSFER); c.facts.vbus=true; c.facts.storage_full=true; rc_core_event(&c,RC_EV_VBUS_OUT,1,&o); show("Q2a TRANSFER vbus_out, storage full");
 rc_core_input(&c,RC_SW_CENTRE,true,2000,&o); tickto(3000); show("Q2b long press with storage_full");
 /* Q3: PAIR: long press via UP+DOWN, then LEFT roll and release all but LEFT; release LEFT at 1500 */
 rc_core_init(&c,RC_CENTRE_PAIR,RC_ST_STANDBY,0); rc_actions_clear(&o);
 rc_core_input(&c,RC_SW_UP,true,0,&o); rc_core_input(&c,RC_SW_DOWN,true,10,&o); rc_core_input(&c,RC_SW_UP,false,200,&o); rc_core_input(&c,RC_SW_LEFT,true,300,&o); rc_core_input(&c,RC_SW_DOWN,false,400,&o); tickto(1010); show("Q3 PAIR roll long"); 
 return 0;}
