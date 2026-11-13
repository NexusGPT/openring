/* Compile check only: touches every public call of ring_sys so the thin part and the real file are linked. */
#include <zephyr/kernel.h>
#include <ring_sys/rsy.h>
#include "rsy_int.h"

int main(void)
{
	struct rrec_crash c;
	uint8_t gp;
	int64_t t;

	(void)rsy_init(NULL);
	(void)rsy_selftest_start(true);
	rsy_selftest_pass(RSY_ITEM_STORAGE);
	(void)rsy_fw_begin(1, 0, 1000, true);
	(void)rsy_fw_data(0, (const uint8_t *)"x", 1);
	(void)rsy_fw_end();
	(void)rsy_factory_flag();
	(void)rsy_time_guess(&t);
	(void)rsy_crash_take(&c, &gp);
	(void)rsy_wdt_start();
	rsy_progress(RSY_THREAD_AUDIO);
	rsy_recording(false);
	rsy_fatal(0, NULL);
	return 0;
}
