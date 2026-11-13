/* Probe F: for every (state, event) and every combination of facts, list the rows whose from, event and guard all match.
 * More than one match = an ordered pair (first row wins in rc_sm_find). Also lists each state's exit rows. */
#include "probe.h"
int main(void) {
  int multi = 0; char seen[200][200]; int ns = 0;
  for (int s = 0; s < RC_ST_COUNT; s++) for (int e = 0; e < RC_EV_COUNT; e++)
    for (int m = 0; m < 2 * 2 * 2 * 2 * 4; m++) {
      struct rc_facts f; memset(&f, 0, sizeof f);
      f.vbus = m & 1; f.open_flag = (m >> 1) & 1; f.factory_flag = (m >> 2) & 1; f.storage_full = (m >> 3) & 1; f.batt = (uint8_t)(m >> 4);
      int rows[8], n = 0;
      for (int i = 0; i < rc_table_rows; i++) {
        const struct rc_row *r = &rc_table[i];
        if (r->from == s && r->event == e && rc_guard_holds((enum rc_guard)r->guard, &f) && n < 8) rows[n++] = r->row;
      }
      if (n > 1) {
        char key[200]; snprintf(key, sizeof key, "%s %s rows", rc_state_name(s), rc_event_name(e));
        for (int k = 0; k < n; k++) { char b[16]; snprintf(b, sizeof b, " %d", rows[k]); strcat(key, b); }
        int dup = 0; for (int k = 0; k < ns; k++) if (!strcmp(seen[k], key)) dup = 1;
        if (!dup && ns < 200) { strcpy(seen[ns++], key);
          printf("OVERLAP %s | first wins: row %d -> %s", key, rows[0], rc_state_name(rc_table[rows[0] - 1].to));
          for (int k = 1; k < n; k++) printf("; row %d -> %s", rows[k], rc_state_name(rc_table[rows[k] - 1].to));
          printf("\n"); }
        multi++;
      }
    }
  printf("SUMMARY overlapping (state,event,facts) cases=%d distinct groups=%d\n", multi, ns);
  for (int s = 0; s < RC_ST_COUNT; s++) {
    printf("EXITS %s:", rc_state_name(s));
    for (int i = 0; i < rc_table_rows; i++) if (rc_table[i].from == s && rc_table[i].to != s) printf(" %d(%s)", rc_table[i].row, rc_event_name(rc_table[i].event));
    printf("\n");
  }
  return 0;
}
