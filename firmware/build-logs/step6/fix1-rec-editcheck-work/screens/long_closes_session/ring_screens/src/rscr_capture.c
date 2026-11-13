/*
 * Ring screens, test hook: reads the frame the display driver received (the panel's 120 x 240 memory, turned back by
 * rscr_from_panel) and writes it as a PNG file. The PNG writer is written here: stored (uncompressed) deflate blocks, no
 * library. Host builds only (native_sim and the simulated chip): files are written through the native simulator's host
 * calls.
 */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include <ring_screens/rscr.h>
#include <ring_screens/rmd.h>

char *nsi_host_getenv(const char *name);
int nsi_host_open(const char *pathname, int flags);
long nsi_host_write(int fd, const void *buffer, unsigned long size);
int nsi_host_close(int fd);

#define HO_WRONLY 1
#define HO_CREAT  0100
#define HO_TRUNC  01000

void rscr_capture_rgb(uint8_t *out)
{
	const uint16_t *fb = rmd_frame();

	for (int y = 0; y < RSCR_H; y++) {
		for (int x = 0; x < RSCR_W; x++) {
			int px, py;
			uint16_t v;

			rscr_to_panel(x, y, &px, &py);
			v = fb[py * RMD_W + px];
			/* RGB565 to RGB888 with the low bits filled from the high bits */
			uint8_t r = (uint8_t)((v >> 11) & 0x1F), g = (uint8_t)((v >> 5) & 0x3F), b = (uint8_t)(v & 0x1F);

			out[(y * RSCR_W + x) * 3 + 0] = (uint8_t)((r << 3) | (r >> 2));
			out[(y * RSCR_W + x) * 3 + 1] = (uint8_t)((g << 2) | (g >> 4));
			out[(y * RSCR_W + x) * 3 + 2] = (uint8_t)((b << 3) | (b >> 2));
		}
	}
}

static uint32_t crc_table[256];

static void crc_init(void)
{
	for (uint32_t n = 0; n < 256; n++) {
		uint32_t c = n;

		for (int k = 0; k < 8; k++) {
			c = (c & 1) ? 0xEDB88320U ^ (c >> 1) : c >> 1;
		}
		crc_table[n] = c;
	}
}

static uint32_t crc_update(uint32_t crc, const uint8_t *p, size_t n)
{
	for (size_t i = 0; i < n; i++) {
		crc = crc_table[(crc ^ p[i]) & 0xFF] ^ (crc >> 8);
	}
	return crc;
}

static int wr(int fd, const void *p, size_t n)
{
	return nsi_host_write(fd, p, n) == (long)n ? 0 : -EIO;
}

static void be32(uint8_t *o, uint32_t v)
{
	o[0] = (uint8_t)(v >> 24);
	o[1] = (uint8_t)(v >> 16);
	o[2] = (uint8_t)(v >> 8);
	o[3] = (uint8_t)v;
}

static int chunk(int fd, const char *type, const uint8_t *data, size_t n)
{
	uint8_t hdr[8], tail[4];
	uint32_t crc = 0xFFFFFFFFU;

	be32(hdr, (uint32_t)n);
	memcpy(hdr + 4, type, 4);
	crc = crc_update(crc, (const uint8_t *)type, 4);
	crc = crc_update(crc, data, n);
	be32(tail, crc ^ 0xFFFFFFFFU);
	if (wr(fd, hdr, 8) != 0 || (n > 0 && wr(fd, data, n) != 0) || wr(fd, tail, 4) != 0) {
		return -EIO;
	}
	return 0;
}

static uint8_t rgb[RSCR_W * RSCR_H * 3];

int rscr_capture_png(const char *path, int scale)
{
	static const uint8_t sig[8] = { 0x89, 'P', 'N', 'G', 0x0D, 0x0A, 0x1A, 0x0A };
	uint8_t ihdr[13];
	int w = RSCR_W * scale, h = RSCR_H * scale;
	size_t rowlen = 1 + (size_t)w * 3;
	size_t total = rowlen * h;
	int fd, rc = 0;
	uint32_t adler_a = 1, adler_b = 0;
	static uint8_t idat[5 + 65535 + 8];

	if (scale < 1 || scale > 4) {
		return -EINVAL;
	}
	crc_init();
	rscr_capture_rgb(rgb);
	fd = nsi_host_open(path, HO_WRONLY | HO_CREAT | HO_TRUNC);
	if (fd < 0) {
		return -EIO;
	}
	be32(ihdr, (uint32_t)w);
	be32(ihdr + 4, (uint32_t)h);
	ihdr[8] = 8;   /* bit depth */
	ihdr[9] = 2;   /* RGB */
	ihdr[10] = ihdr[11] = ihdr[12] = 0;
	rc |= wr(fd, sig, 8);
	rc |= chunk(fd, "IHDR", ihdr, 13);

	/* The zlib stream is split over several IDAT chunks of at most 65535 stored bytes each: build the stream
	 * piece by piece. Piece = (2 byte zlib header, first piece only) + stored block headers + data. To keep it
	 * simple every IDAT chunk holds exactly one stored deflate block. */
	{
		size_t off = 0;
		bool first = true;

		while (off < total && rc == 0) {
			size_t n = total - off > 65535 ? 65535 : total - off;
			bool last = off + n == total;
			size_t k = 0;

			if (first) {
				idat[k++] = 0x78;
				idat[k++] = 0x01;
				first = false;
			}
			idat[k++] = last ? 1 : 0;
			idat[k++] = (uint8_t)(n & 0xFF);
			idat[k++] = (uint8_t)(n >> 8);
			idat[k++] = (uint8_t)(~n & 0xFF);
			idat[k++] = (uint8_t)((~n >> 8) & 0xFF);
			for (size_t i = 0; i < n; i++) {
				size_t pos = off + i;
				size_t row = pos / rowlen, col = pos % rowlen;
				uint8_t v;

				if (col == 0) {
					v = 0;   /* filter none */
				} else {
					size_t px = (col - 1) / 3, ch = (col - 1) % 3;
					size_t sx = px / scale, sy = row / scale;

					v = rgb[(sy * RSCR_W + sx) * 3 + ch];
				}
				idat[k++] = v;
				adler_a = (adler_a + v) % 65521U;
				adler_b = (adler_b + adler_a) % 65521U;
			}
			if (last) {
				uint32_t ad = (adler_b << 16) | adler_a;

				be32(idat + k, ad);
				k += 4;
			}
			rc |= chunk(fd, "IDAT", idat, k);
			off += n;
		}
	}
	rc |= chunk(fd, "IEND", NULL, 0);
	(void)nsi_host_close(fd);
	return rc;
}
