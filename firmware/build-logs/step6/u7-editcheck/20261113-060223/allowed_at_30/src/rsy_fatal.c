/*
 * rsy_fatal.c: the override of the kernel's fatal error handler (FW l.1063). Written for this project. Built only
 * when CONFIG_RING_SYS_FATAL_HANDLER is set (not in test builds, which carry the test framework's own handler).
 */
#include <zephyr/kernel.h>
#include <zephyr/fatal.h>

#include "rsy_int.h"

FUNC_NORETURN void k_sys_fatal_error_handler(unsigned int reason, const struct arch_esf *esf)
{
	rsy_fatal(reason, esf);
	/* the reboot request does not return on the real chip; if it ever does, wait for the watchdog */
	for (;;) {
		k_cpu_idle();
	}
}
