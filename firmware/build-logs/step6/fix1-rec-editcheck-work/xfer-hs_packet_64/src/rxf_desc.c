/*
 * rxf_desc.c: the pure part of the vendor class: the full-speed and high-speed descriptor tables (FW l.669).
 * Written for this project. No kernel call.
 */
#include <string.h>

#include "rxf_desc.h"

#define DESC_TYPE_INTERFACE 0x04u   /* USB 2.0 table 9-5 */
#define DESC_TYPE_ENDPOINT 0x05u    /* USB 2.0 table 9-5 */
#define EP_ATTR_BULK 0x02u          /* USB 2.0 table 9-13 */

uint16_t rxf_desc_mps(enum rhw_usb_speed speed)
{
	return speed == RHW_USB_HS ? (uint16_t)RREC_USB_MPS_FS : (uint16_t)RREC_USB_MPS_FS;
}

size_t rxf_desc_get(enum rhw_usb_speed speed, uint8_t out[RXF_DESC_BYTES])
{
	uint16_t mps = rxf_desc_mps(speed);
	const uint8_t eps[2] = { RREC_USB_EP_OUT, RREC_USB_EP_IN };
	uint8_t *p = out;

	/* interface: length 9, type 4, number 0 (the stack assigns it), alternate 0, 2 endpoints, class, subclass,
	 * protocol, no string */
	*p++ = 9u;
	*p++ = DESC_TYPE_INTERFACE;
	*p++ = 0u;
	*p++ = 0u;
	*p++ = 2u;
	*p++ = RREC_USB_CLASS;
	*p++ = RREC_USB_SUBCLASS;
	*p++ = RREC_USB_PROTOCOL;
	*p++ = 0u;
	for (int i = 0; i < 2; i++) {
		*p++ = 7u;
		*p++ = DESC_TYPE_ENDPOINT;
		*p++ = eps[i];
		*p++ = EP_ATTR_BULK;
		*p++ = (uint8_t)mps;
		*p++ = (uint8_t)(mps >> 8);
		*p++ = 0u;                      /* bulk: no interval */
	}
	return (size_t)(p - out);
}
