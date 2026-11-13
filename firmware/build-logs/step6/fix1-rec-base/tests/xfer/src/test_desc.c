/*
 * test_desc.c: suite xfer_desc (unit U4): the descriptor tables of the vendor class (rxf_desc.c).
 * Rows X2 and X22 of firmware/docs/step6-plan.md. Expected bytes are typed from design/firmware.md l.669 (class 0xFF,
 * subclass 0x00, protocol 0x00, bulk OUT 0x01, bulk IN 0x81, 64 bytes at full speed, 512 at high speed) and the
 * USB 2.0 descriptor formats (interface: 9 bytes, type 4; endpoint: 7 bytes, type 5, bulk = 2).
 */
#include "xt.h"

ZTEST_SUITE(xfer_desc, NULL, NULL, NULL, NULL, NULL);

/* X2: the full-speed and high-speed tables, byte by byte */
ZTEST(xfer_desc, test_descriptor_bytes_fs_hs)
{
	uint8_t d[RXF_DESC_BYTES];
	const uint8_t fs[23] = {
		0x09, 0x04, 0x00, 0x00, 0x02, 0xFF, 0x00, 0x00, 0x00,    /* interface 0, 2 endpoints, 0xFF/0x00/0x00 */
		0x07, 0x05, 0x01, 0x02, 0x40, 0x00, 0x00,                /* OUT 0x01, bulk, 64 */
		0x07, 0x05, 0x81, 0x02, 0x40, 0x00, 0x00,                /* IN 0x81, bulk, 64 */
	};
	const uint8_t hs[23] = {
		0x09, 0x04, 0x00, 0x00, 0x02, 0xFF, 0x00, 0x00, 0x00,
		0x07, 0x05, 0x01, 0x02, 0x00, 0x02, 0x00,                /* OUT 0x01, bulk, 512 = 0x0200 */
		0x07, 0x05, 0x81, 0x02, 0x00, 0x02, 0x00,                /* IN 0x81, bulk, 512 */
	};

	memset(d, 0xEE, sizeof(d));
	zassert_equal(rxf_desc_get(RHW_USB_FS, d), 23u);
	zassert_mem_equal(d, fs, sizeof(fs), "full speed table");
	memset(d, 0xEE, sizeof(d));
	zassert_equal(rxf_desc_get(RHW_USB_HS, d), 23u);
	zassert_mem_equal(d, hs, sizeof(hs), "high speed table");
	zassert_equal(rxf_desc_mps(RHW_USB_FS), 64u);
	zassert_equal(rxf_desc_mps(RHW_USB_HS), 512u);
}

/* X22: one vendor interface, no mass storage class and no serial class: the case reads only through the protocol */
ZTEST(xfer_desc, test_one_vendor_interface_only)
{
	enum rhw_usb_speed sp[] = { RHW_USB_FS, RHW_USB_HS };

	for (unsigned s = 0; s < 2; s++) {
		uint8_t d[RXF_DESC_BYTES];
		unsigned ifaces = 0, eps = 0, off = 0, in_n = 0, out_n = 0;
		size_t n = rxf_desc_get(sp[s], d);

		while (off < n) {
			uint8_t len = d[off], type = d[off + 1];

			zassert_true(len >= 2 && off + len <= n, "well formed at offset %u", off);
			if (type == 0x04) {
				ifaces++;
				zassert_equal(d[off + 5], 0xFF, "vendor class");
				zassert_not_equal(d[off + 5], 0x08, "not mass storage");
				zassert_not_equal(d[off + 5], 0x02, "not communications (serial)");
				zassert_not_equal(d[off + 5], 0x0A, "not CDC data");
				zassert_equal(d[off + 6], 0x00);
				zassert_equal(d[off + 7], 0x00);
				zassert_equal(d[off + 4], 2u, "two endpoints");
			} else if (type == 0x05) {
				eps++;
				zassert_equal(d[off + 3] & 0x03, 0x02, "bulk");
				if (d[off + 2] == 0x01) {
					out_n++;
				}
				if (d[off + 2] == 0x81) {
					in_n++;
				}
			} else {
				zassert_unreachable("a descriptor of type %02x in the class's table", type);
			}
			off += len;
		}
		zassert_equal(ifaces, 1u, "exactly one interface");
		zassert_equal(eps, 2u);
		zassert_equal(out_n, 1u);
		zassert_equal(in_n, 1u);
	}
}
