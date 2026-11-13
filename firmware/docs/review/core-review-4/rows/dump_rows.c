/* Review 2 probe: for every table row, put the core in the row's from-state with facts that satisfy
 * the row's guard (and no earlier row's), take the event through rc_sm_handle, print row, from, event_text, guard, to, actions. */
#include <stdio.h>
#include <string.h>
#include "ring_core/rc_core.h"
static void facts_for(struct rc_facts *f, enum rc_guard g, int variant) {
  memset(f,0,sizeof *f); f->vibration_on=true; f->batt=RC_BATT_OK; f->screen_on=(variant==1);
  switch(g){
   case RC_G_OPEN_SET: f->open_flag=true; break;
   case RC_G_VBUS: f->vbus=true; break;
   case RC_G_NO_VBUS: break;
   case RC_G_SFULL: case RC_G_SFULL_ABOVE_B5: f->storage_full=true; break;
   case RC_G_AT_B5: f->batt=RC_BATT_B5; break;
   case RC_G_AT_B2: f->batt=RC_BATT_B2; break;
   case RC_G_FACTORY_FLAG: f->factory_flag=true; break;
   default: break;
  }
  if (variant==2) f->open_flag=true; /* row 57 */
}
int main(void){
  for (int i=0;i<rc_table_rows;i++){
    const struct rc_row *r=&rc_table[i];
    for (int v=0; v<3; v++){
      if (v==1 && r->row!=16) continue;
      if (v==2) continue;
      struct rc_sm sm; struct rc_facts f; struct rc_actions a;
      rc_sm_init(&sm,(enum rc_state)r->from); facts_for(&f,(enum rc_guard)r->guard,v); rc_actions_clear(&a);
      int got=rc_sm_handle(&sm,(enum rc_event)r->event,&f,&a);
      printf("%d|%s|%s|%s|%s|got=%d|%s|",r->row,rc_state_name(r->from),r->event_text,rc_guard_name(r->guard),rc_state_name(r->to),got,rc_state_name(sm.state));
      for(int k=0;k<a.n;k++) printf("%s%s",k?" ":"",rc_action_name(a.a[k]));
      printf("|v%d\n",v);
    }
  }
  return 0;
}
