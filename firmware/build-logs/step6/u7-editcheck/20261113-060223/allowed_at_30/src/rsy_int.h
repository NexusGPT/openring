/*
 * rsy_int.h: the thin part's own entry points that other files of this unit and its tests use (not a public header).
 * The fatal error path is split so a test can run it: the test framework defines k_sys_fatal_error_handler() itself,
 * so rsy_fatal.c (the override) is left out of test builds and a test calls these two functions instead.
 */
#ifndef RING_SYS_RSY_INT_H
#define RING_SYS_RSY_INT_H

#include <stddef.h>
#include <stdint.h>

#include <zephyr/fatal.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Build the crash block of FW l.1063 and write it into retained memory (no lock, no wait: allowed in the fatal error
 * handler). thread: NUL-terminated, kept to RREC_CRASH_NAME_BYTES - 1 characters; NULL gives "?". stack: the faulting
 * stack's words from its start (NULL or 0 words: the rest of the 64 words is zero). Returns the retained write's
 * result. */
int rsy_crash_capture(uint32_t reason, uint32_t pc, uint32_t lr, uint32_t psr, const char *thread,
		      const uint32_t *stack, size_t stack_words);
/* The whole fatal path of FW l.1063: take the registers of the exception frame, capture, put the reason code into
 * gpregret1, request the reboot (RHW_REBOOT_CRASH). Returns after the reboot request (the real one does not return;
 * the simulated one does). esf may be NULL (registers read as 0). */
void rsy_fatal(unsigned int reason, const struct arch_esf *esf);

#ifdef __cplusplus
}
#endif

#endif
