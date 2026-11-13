/* glue.h: a backend for rxf.h that fills its calls from the store's real code (ring_store) on the simulated card.
 * It stands for the join (ring_recorder), which is another unit's; the layouts of GET_INFO and of the list entries are
 * typed here from design/firmware.md l.696 and l.697 (the RREC_GI_OFF_* and RREC_LE_OFF_* offsets of rrec_spec.h). */
#ifndef GLUE_H
#define GLUE_H

#include <ring_store/rst.h>
#include <ring_xfer/rxf.h>

#define GLUE_FW_VERSION 0x00010203u

struct glue_seen {
	int64_t utc_ms;
	int16_t tz;
	uint32_t after_calls;
	uint8_t after_op;
	uint32_t time_calls;
	bool factory_flag;
	uint32_t boot_count;
};
extern struct glue_seen gl;

const struct rxf_backend *glue_be(void);
void glue_reset(void);

#endif
