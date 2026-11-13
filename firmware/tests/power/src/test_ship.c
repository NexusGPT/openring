/* Suite power_ship (software step 6, unit U5): ship mode entry steps 2 to 5 of FW 8.4 (l.936 to l.941).
 * Rows P12 and P13. rpw_ship() is called in the test thread. After the simulated ship task every driver call is
 * refused and counted (the simulated chip's "no supply"); the real chip would stop the ring there. */
#include <errno.h>
#include <string.h>

#include "common.h"

ZTEST_SUITE(power_ship, NULL, NULL, pw_before, NULL, NULL);

static volatile uint32_t hook_calls;
static volatile uint32_t hook_log_n;

static void hook(void)
{
	hook_calls++;
	hook_log_n = rhw_sim_log_count();
}

/* the first task finds a case pushed on during the hook: VBUS present at the chip, removed 1.5 s later */
static void hook_vbus_back(void)
{
	hook_calls++;
	rhw_sim_pmic_vbus(true);
	rhw_sim_vbus_at(k_uptime_get() + 1500, false);
}

/* kinds that may stand between two entries */
static bool only_kinds(uint32_t from, uint32_t to, uint16_t k1, uint16_t k2)
{
	for (uint32_t i = from; i < to; i++) {
		uint16_t kd = pw_ev(i).kind;

		if (kd != k1 && kd != k2) {
			return false;
		}
	}
	return true;
}

/* FW l.936 to l.940, no VBUS: SHPHLDCONFIG at 96 ms, the strobe, then (the beacon hook), then the task. Nothing else
 * in between, no sample while it runs. */
ZTEST(power_ship, test_entry_order_without_vbus)
{
	int32_t cfg, str, task;

	pw_script1(3900, 0);
	rpw_state(RC_ST_RECORDING);         /* 1 s sampling: it must stop while the ship steps run */
	pw_start();
	rhw_sim_log_clear();
	hook_calls = 0;
	zassert_equal(rpw_ship(hook), -ETIMEDOUT, "the simulated chip cannot cut the supply for real: returns");
	cfg = pw_find(RHW_EV_PMIC_SHPHLD_CFG, 0);
	zassert_true(cfg >= 0, "SHPHLDCONFIG written");
	str = pw_find(RHW_EV_PMIC_SHPHLD_STROBE, cfg);
	zassert_true(str > cfg, "the strobe follows the configuration");
	task = pw_find(RHW_EV_PMIC_SHIP, str);
	zassert_true(task > str, "the task follows the strobe");
	zassert_equal(pw_ev(cfg).a0, 96, "FW l.938: the default press time, 96 ms");
	zassert_equal(pw_ev(task).a0, 0, "no VBUS at the task");
	zassert_equal(task, cfg + 2, "nothing between the three writes");
	zassert_equal(hook_calls, 1, "the beacon hook runs once");
	zassert_equal(hook_log_n, (uint32_t)task, "the hook runs right before the task");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SHIP), 1, "one task that reached the chip");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SAMPLE), 0, "no sample during the ship steps");

	/* the step machine, no VBUS: the same order, then the one retry (FW l.936 to l.941), the beacon hook only once */
	{
		struct rpwl_ship s;

		rpwl_ship_reset(&s);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_CONFIG);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_STROBE);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_BEFORE_TASK);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_TASK);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_WAIT_1S);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_LOG_RETRY);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_TASK, "the retry has no second hook");
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_WAIT_1S);
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_GIVE_UP, "the retry is once");
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_GIVE_UP);
	}
}

/* FW l.939: with VBUS, wait for VBUS removed, doing nothing else; the task only after it.
 * Part A: VBUS present from the start, removed 700 ms after the call. Part B: the first task finds VBUS back (a case
 * pushed on during the hook): 1 s later the retry goes back to step 3 and waits again before the second task. */
ZTEST(power_ship, test_waits_for_vbus_removed)
{
	int32_t cfg, out, task, task2;
	int64_t t;

	/* part A */
	rhw_sim_pmic_vbus(true);
	pw_script1(3900, 0);
	pw_start();
	k_sleep(K_MSEC(20));
	rhw_sim_log_clear();
	t = k_uptime_get();
	rhw_sim_vbus_at(t + 700, false);
	zassert_equal(rpw_ship(hook), -ETIMEDOUT);
	cfg = pw_find(RHW_EV_PMIC_SHPHLD_CFG, 0);
	out = pw_find(RHW_EV_PMIC_VBUS, cfg);
	zassert_true(cfg >= 0 && out > cfg, "VBUS removed after the configuration");
	zassert_equal(pw_ev(out).a0, 0);
	task = pw_find(RHW_EV_PMIC_SHIP, 0);
	zassert_true(task > out, "the task was written after VBUS went (entry %d, VBUS entry %d)", task, out);
	zassert_equal(pw_ev(task).a0, 0, "VBUS absent at the task");
	zassert_true(only_kinds(cfg + 1, out, RHW_EV_PMIC_SHPHLD_STROBE, RHW_EV_PMIC_SHPHLD_STROBE),
		     "while it waits the ring does nothing else");
	zassert_true(pw_ev(task).t_us - pw_ev(cfg).t_us >= 690000, "it waited for the removal");

	/* the step machine: with VBUS present it keeps answering "wait", after the two writes of step 2 */
	{
		struct rpwl_ship s;

		rpwl_ship_reset(&s);
		(void)rpwl_ship_next(&s, true);
		(void)rpwl_ship_next(&s, true);
		zassert_equal(rpwl_ship_next(&s, true), RPWL_SHIP_WAIT_VBUS);
		zassert_equal(rpwl_ship_next(&s, true), RPWL_SHIP_WAIT_VBUS, "keeps waiting while VBUS is present");
		zassert_equal(rpwl_ship_next(&s, false), RPWL_SHIP_BEFORE_TASK, "task only after VBUS went");
	}

	/* part B */
	pw_before(NULL);
	pw_script1(3900, 0);
	pw_start();
	rhw_sim_log_clear();
	memset(&cap, 0, sizeof(cap));
	t = k_uptime_get();
	zassert_equal(rpw_ship(hook_vbus_back), -ETIMEDOUT);
	task = pw_find(RHW_EV_PMIC_SHIP, 0);
	zassert_true(task >= 0);
	zassert_equal(pw_ev(task).a0, 1, "the first task met VBUS: the simulated chip stays up");
	out = pw_find(RHW_EV_PMIC_VBUS, task);
	zassert_true(out > task && pw_ev(out).a0 == 0, "VBUS removed after the first task");
	task2 = pw_find(RHW_EV_PMIC_SHIP, task + 1);
	zassert_true(task2 > out, "the second task waited for VBUS removed (entry %d, VBUS entry %d)", task2, out);
	zassert_equal(pw_ev(task2).a0, 0, "VBUS absent at the second task");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SHIP), 2, "two tasks, no third");
	zassert_equal(pw_log_count(RREC_LOG_SHIP_RETRY), 1);
	zassert_within(cap.log[0].t_ms - pw_ev(task).t_us / 1000, 1000, 2, "the retry is logged 1 s after the first task");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SAMPLE), 0, "no sample while it waits");
}

/* FW l.941: still running 1 s after the task: log, back to step 3 once. No VBUS: the retry's task is refused by
 * the simulated chip (no supply); the call returns -ETIMEDOUT after the second try, 2 s after the first task. */
ZTEST(power_ship, test_retry_once_after_1s)
{
	int32_t task, refused;
	int64_t t_start, t_end;

	pw_start();
	rhw_sim_log_clear();
	t_start = k_uptime_get();
	zassert_equal(rpw_ship(NULL), -ETIMEDOUT);
	t_end = k_uptime_get();
	task = pw_find(RHW_EV_PMIC_SHIP, 0);
	zassert_true(task >= 0);
	zassert_equal(pw_log_count(RREC_LOG_SHIP_RETRY), 1, "one retry record");
	zassert_equal(cap.log[0].code, 0x0250);
	zassert_equal(cap.log[0].n, 1);
	zassert_equal(cap.log[0].args[0], 1, "try 1");
	zassert_within(cap.log[0].t_ms - pw_ev(task).t_us / 1000, 1000, 2, "logged 1 s after the task");
	refused = pw_find(RHW_EV_SHIP_REFUSED, task);
	zassert_true(refused > task, "the second task was tried");
	zassert_equal(pw_ev(refused).a0, RHW_EV_PMIC_SHIP, "what was refused is the task");
	zassert_within(pw_ev(refused).t_us - pw_ev(task).t_us, 1000000, 2000, "the retry comes 1 s after");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SHIP), 1);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_SHIP_REFUSED), 1, "once, not more");
	zassert_within(t_end - t_start, 2000, 20, "two tries of 1 s each");
}

/* FW l.939: only the factory commands reach step 3 with VBUS present; every row into OFF starts without VBUS.
 * Without VBUS the call never waits: the three writes come in the same instant. */
ZTEST(power_ship, test_off_never_waits)
{
	int32_t cfg, task;

	pw_start();
	rhw_sim_log_clear();
	zassert_equal(rpw_ship(NULL), -ETIMEDOUT);
	cfg = pw_find(RHW_EV_PMIC_SHPHLD_CFG, 0);
	task = pw_find(RHW_EV_PMIC_SHIP, cfg);
	zassert_true(cfg >= 0 && task > cfg);
	zassert_true(pw_ev(task).t_us - pw_ev(cfg).t_us < 10000, "no wait before the task");
	zassert_true(only_kinds(cfg + 1, task, RHW_EV_PMIC_SHPHLD_STROBE, RHW_EV_PMIC_SHPHLD_STROBE));
}
