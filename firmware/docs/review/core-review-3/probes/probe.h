#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "ring_core/rc_core.h"
static struct rc_core C; static struct rc_actions A;
static int npass, nfail;
#define CHECK(name, cond) do { if (cond) { npass++; printf("PASS %s\n", name); } else { nfail++; printf("FAIL %s\n", name); } } while (0)
static void init(enum rc_state st, enum rc_centre_source src) { rc_core_init(&C, src, st, 0); rc_actions_clear(&A); }
static void ev(enum rc_event e, rc_ms_t t) { rc_actions_clear(&A); rc_core_event(&C, e, t, &A); }
static void sw(enum rc_switch s, bool p, rc_ms_t t) { rc_actions_clear(&A); rc_core_input(&C, s, p, t, &A); }
static void tk(rc_ms_t t) { rc_actions_clear(&A); rc_core_tick(&C, t, &A); }
static void bt(enum rc_batt l, rc_ms_t t) { rc_actions_clear(&A); rc_core_battery(&C, l, t, &A); }
static bool has(enum rc_action a) { for (int i = 0; i < A.n; i++) if (A.a[i] == a) return true; return false; }
static int cnt(enum rc_action a) { int n = 0; for (int i = 0; i < A.n; i++) if (A.a[i] == a) n++; return n; }
static enum rc_state S(void) { return rc_core_state(&C); }
static const char *SN(void) { return rc_state_name(S()); }
static struct rc_facts *F(void) { return rc_core_facts(&C); }
static void acts(void) { for (int i = 0; i < A.n; i++) printf("%s ", rc_action_name(A.a[i])); }
