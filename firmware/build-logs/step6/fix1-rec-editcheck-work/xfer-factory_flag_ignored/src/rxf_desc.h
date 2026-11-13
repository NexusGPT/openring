/*
 * rxf_desc.h: the pure descriptor tables of the vendor class (software step 6, unit U4). Not public. No kernel call.
 * FW l.669: one interface 0xFF/0x00/0x00, bulk OUT 0x01, bulk IN 0x81, wMaxPacketSize 64 at full speed and 512 at high
 * speed. The stack numbers the interface and builds the configuration descriptor around these bytes.
 */
#ifndef RXF_DESC_H
#define RXF_DESC_H

#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rhw.h>

#define RXF_DESC_BYTES 23u      /* interface descriptor (9) + two endpoint descriptors (7 each) */

/* The class's descriptors for the speed: written to out (RXF_DESC_BYTES). Returns RXF_DESC_BYTES. */
size_t rxf_desc_get(enum rhw_usb_speed speed, uint8_t out[RXF_DESC_BYTES]);

/* wMaxPacketSize of the bulk endpoints at the speed. */
uint16_t rxf_desc_mps(enum rhw_usb_speed speed);

#endif
