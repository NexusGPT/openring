/* Suite factory_store (software step 6, unit U8): T-STORE (0x50, FW l.1030): VDD_SD on, init, write 65 sectors at LBA
 * 4,096, read back, compare the CRC, time both; then delete every test recording (type 2). Rows T18.
 * Expected values are typed from FW l.1030 (LBA 4,096, 65 sectors) and l.548 (type 2). Speeds: not provable here. */
#include "common.h"

ZTEST_SUITE(factory_store, NULL, NULL, fx_before, fx_after, NULL);

#define FAC_LBA 4096     /* FW l.1030 */
#define FAC_SECTORS 65   /* FW l.1030 */

ZTEST(factory_store, test_area_write_read)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	rhw_sim_disk_stall_ms(20); /* a card that takes 20 ms per write: the write time must show it */
	rhw_sim_log_clear();
	zassert_equal(fx_do1(0x50, true, out, &n, &eff), 0);
	zassert_equal(n, 14, "T-STORE answers 14 bytes");
	zassert_equal(out[0], 0, "pass");
	zassert_equal(out[1], 1, "data equal");
	zassert_true(fx_u32(&out[2]) >= 20000, "the write took %u us (the card stalls 20 ms)", fx_u32(&out[2]));
	zassert_true(fx_u32(&out[2]) < 40000, "write time %u us", fx_u32(&out[2]));
	zassert_equal(fx_u32(&out[10]), 0, "no test recording to delete");

	/* the one write and the one read of the area, in the simulated card's log */
	uint32_t area_writes = 0, area_reads = 0;
	struct rhw_sim_ev e;
	int32_t w = -1, r = -1;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		if (e.kind == RHW_EV_DISK_WRITE && e.a1 == FAC_SECTORS) {
			zassert_equal(e.a0, FAC_LBA, "the area is written at LBA 4,096, not %lld", e.a0);
			area_writes++;
			w = (int32_t)i;
		}
		if (e.kind == RHW_EV_DISK_READ && e.a1 == FAC_SECTORS) {
			zassert_equal(e.a0, FAC_LBA, "the area is read at LBA 4,096, not %lld", e.a0);
			area_reads++;
			r = (int32_t)i;
		}
	}
	zassert_equal(area_writes, 1, "one write of 65 sectors");
	zassert_equal(area_reads, 1, "one read of 65 sectors");
	zassert_true(w >= 0 && r > w, "read after write");
	/* VDD_SD on before the area is touched (the card refuses a call with the rail off) */
	int32_t sd_on = -1;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		if (e.kind == RHW_EV_PMIC_RAIL && e.a0 == RHW_RAIL_SD && e.a1 != 0) {
			sd_on = (int32_t)i;
			break;
		}
	}
	zassert_true(sd_on >= 0 && sd_on < w, "VDD_SD on, then the write");
	zassert_equal(rhw_sim_disk_refused(), 0, "the card refused no call");
	zassert_false(rst_mounted(), "the card was not mounted before: it is left as it was");
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD), "VDD_SD off again");

	/* a card that cannot be read at the area: the test fails */
	rhw_sim_disk_read_error_at(FAC_LBA);
	zassert_equal(fx_do1(0x50, true, out, &n, &eff), 0);
	zassert_equal(out[0], 1, "read error: fail");
	rhw_sim_disk_read_error_at(UINT32_MAX);

	/* a card that was already mounted stays mounted */
	zassert_ok(rst_mount(false, &(struct rst_mount_info){ 0 }));
	zassert_equal(fx_do1(0x50, true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_true(rst_mounted(), "mounted before, mounted after");
	zassert_ok(rst_unmount());
}

/* T18: then delete every test recording (type 2) the jig made; a recording of the wearer stays. */
ZTEST(factory_store, test_test_recordings_deleted)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	struct rst_rec_info list[8];
	uint16_t count = 0;
	int64_t on, off;

	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -20);
	/* a recording of the wearer (type 1) and two test recordings (type 2, made by T-SIGN) */
	fx_rec_type = RREC_REC_TYPE_RECORDING;
	zassert_ok(fx_test_recording(500, NULL, &on, &off));
	fx_rec_type = RREC_REC_TYPE_FACTORY;
	zassert_equal(fx_do1(0x41, true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_ok(rst_mount(false, &(struct rst_mount_info){ 0 }));
	zassert_ok(rst_list(0, 8, list, &count));
	zassert_equal(count, 3, "three recordings before T-STORE");
	zassert_ok(rst_unmount());

	zassert_equal(fx_do1(0x50, true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_equal(fx_u32(&out[10]), 2, "two test recordings deleted");

	zassert_ok(rst_mount(false, &(struct rst_mount_info){ 0 }));
	zassert_ok(rst_list(0, 8, list, &count));
	zassert_equal(count, 1, "no test recording left");
	zassert_equal(list[0].type, 1, "the wearer's recording stays");
	zassert_ok(rst_unmount());

	/* a second T-STORE finds nothing more to delete */
	zassert_equal(fx_do1(0x50, true, out, &n, &eff), 0);
	zassert_equal(fx_u32(&out[10]), 0);
}
