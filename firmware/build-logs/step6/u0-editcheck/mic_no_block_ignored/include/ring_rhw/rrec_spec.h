/*
 * rrec_spec.h: the numbers of the recorder parts (software step 6), each defined once, each with the line of the
 * specification it comes from. "FW l.N" = line N of design/firmware.md at commit 783ddc4 of the project.
 *
 * Rule (step 6 plan, unit U0): a number that more than one unit of step 6 uses is defined here and nowhere else.
 * A unit that needs another such number asks the lead; U0 adds it here. Pure C: no include beyond stdint.
 *
 * Not here on purpose:
 *  - CHARGE_CURRENT (FW l.878, l.894): the one named constant lives in ring_power (U5) with its build assertions,
 *    so that its broken copies change one place; other units read it through rpw_charge_current_ua() (rpw.h).
 *  - The motor soft start (lead's ruling D3: not built in step 6): no constant.
 *  - Chip pins: none, ever (FW l.77; pins come from the board files of step 7).
 */
#ifndef RING_RHW_RREC_SPEC_H
#define RING_RHW_RREC_SPEC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ------------------------------------------------------------------ general (FW l.70) */
/* All multi-byte fields little-endian; every CRC-32 is CRC-32/ISO-HDLC = Zephyr crc32_ieee() (FW l.70). */
#define RREC_CRC32_CHECK_VALUE        0xCBF43926u  /* CRC-32/ISO-HDLC of "123456789" (catalogue check value; test S8) */

/* ------------------------------------------------------------------ audio, FW 4 */
#define RREC_PCM_RATE_HZ              16000u      /* FW l.411 */
#define RREC_PCM_WIDTH_BITS           16u         /* FW l.412 */
#define RREC_CHANNELS                 2u          /* FW l.413 */
#define RREC_PDM_CLK_MIN_HZ           1200000u    /* FW l.415 */
#define RREC_PDM_CLK_MAX_HZ           1650000u    /* FW l.415 */
#define RREC_PDM_CLOCK_HZ             1280000u    /* FW l.416, header field pdm_clock_hz FW l.560 */
#define RREC_PDM_RATIO                80u         /* FW l.416, header field pdm_ratio FW l.561 */
#define RREC_PDM_GAIN_DB              0           /* FW l.417 */
#define RREC_PDM_GAIN_CODE            0x28u       /* FW l.417, header field gain_code FW l.562 */
#define RREC_BLOCK_BYTES              1024u       /* FW l.419 */
#define RREC_BLOCK_FRAMES             256u        /* FW l.419: 256 stereo frames */
#define RREC_BLOCK_MS                 16u         /* FW l.419, l.436 */
#define RREC_BLOCK_COUNT              8u          /* FW l.420: slab of 8 blocks (queue-size) */
#define RREC_BLOCKS_PER_CHUNK         32u         /* FW l.443: "After 32 blocks the chunk is full" */
#define RREC_CHUNK_RING               3u          /* FW l.440, l.490: never below 3 chunks */
#define RREC_DISCARD_MS               50u         /* FW l.460 */
#define RREC_DISCARD_FRAMES           800u        /* FW l.460: 50 ms at 16 kHz */
#define RREC_MIC_RAIL_WAIT_MS         1u          /* FW l.458: wait 1 ms after VDD_MIC on */
#define RREC_MIC_NO_BLOCK_MS          100u        /* FW l.108, l.169: no block for 100 ms = ERR_MIC_FAULT */
#define RREC_MOTOR_TAIL_MS            50u         /* FW l.495: interval ends 50 ms after MOTOR low */
#define RREC_MOTOR_TAIL_FRAMES        800u        /* FW l.495 */
#define RREC_LONG_PRESS_MS            1000u       /* FW l.128, l.448: stop keeps the frames up to this mark */

/* ------------------------------------------------------------------ storage layout, FW 5.2 */
#define RREC_SECTOR_BYTES             512u        /* FW l.519 */
#define RREC_LBA_SB_A                 0u          /* FW l.523 */
#define RREC_LBA_SB_B                 1u          /* FW l.524 */
#define RREC_LBA_LOG_FIRST            2u          /* FW l.525 */
#define RREC_LBA_LOG_LAST             2047u       /* FW l.525 */
#define RREC_LOG_RING_RECORDS         2046u       /* FW l.525: ring of 2,046 records, 1 per sector */
#define RREC_LBA_RESERVED1_FIRST      2048u       /* FW l.526 */
#define RREC_LBA_RESERVED1_LAST       8191u       /* FW l.526 */
#define RREC_LBA_FACTORY_FIRST        4096u       /* FW l.526, l.1030: T-STORE writes 65 sectors at LBA 4,096 */
#define RREC_LBA_FACTORY_LAST         4160u       /* FW l.526 */
#define RREC_FACTORY_SECTORS          65u         /* FW l.1030 */
#define RREC_LBA_INDEX_FIRST          8192u       /* FW l.527 */
#define RREC_LBA_INDEX_LAST           73727u      /* FW l.527 */
#define RREC_INDEX_RING_RECORDS       65536u      /* FW l.527, l.612 */
#define RREC_LBA_RESERVED2_FIRST      73728u      /* FW l.528 */
#define RREC_LBA_RESERVED2_LAST       81919u      /* FW l.528 */
#define RREC_LBA_CHUNK_FIRST          81920u      /* FW l.529, l.531; superblock field FW l.596 */
#define RREC_CHUNK_SECTORS            65u         /* FW l.529, l.535: 1 header + 64 payload sectors */
#define RREC_CHUNK_PAYLOAD_SECTORS    64u         /* FW l.535 */
#define RREC_CHUNK_BYTES              33280u      /* FW l.535 */
#define RREC_CHUNK_HEADER_BYTES       512u        /* FW l.535, l.543 */
#define RREC_CHUNK_PAYLOAD_BYTES      32768u      /* FW l.535 */
#define RREC_CHUNK_FRAMES             8192u       /* FW l.535: 512 ms at 16 kHz, 2 channels */
#define RREC_CHUNK_MS                 512u        /* FW l.535, l.653 */
/* chunk_count_total = floor((sectors - RREC_LBA_CHUNK_FIRST) / RREC_CHUNK_SECTORS) (FW l.529);
 * chunk s starts at RREC_LBA_CHUNK_FIRST + (s mod chunk_count_total) x RREC_CHUNK_SECTORS (FW l.531);
 * index record n at RREC_LBA_INDEX_FIRST + (n mod RREC_INDEX_RING_RECORDS) (FW l.612). Units compute these in ring_store. */

/* ------------------------------------------------------------------ chunk header, FW 5.3 (offsets in bytes) */
#define RREC_CHUNK_MAGIC              0x4B435252u /* "RRCK", FW l.541 */
#define RREC_CHUNK_HEADER_VERSION     1u          /* FW l.542 */
#define RREC_CH_OFF_MAGIC             0u          /* FW l.541 */
#define RREC_CH_OFF_VERSION           4u          /* FW l.542 */
#define RREC_CH_OFF_SIZE              6u          /* FW l.543 */
#define RREC_CH_OFF_CHUNK_SEQ         8u          /* FW l.544 */
#define RREC_CH_OFF_RECORDING_ID      12u         /* FW l.545 */
#define RREC_CH_OFF_CHUNK_IN_REC      16u         /* FW l.546 */
#define RREC_CH_OFF_FLAGS             20u         /* FW l.547 */
#define RREC_CH_OFF_RECORDING_TYPE    22u         /* FW l.548 */
#define RREC_CH_OFF_CHANNELS          23u         /* FW l.549 */
#define RREC_CH_OFF_SAMPLE_RATE       24u         /* FW l.550 */
#define RREC_CH_OFF_SAMPLE_FORMAT     28u         /* FW l.551 */
#define RREC_CH_OFF_MIC_MASK          29u         /* FW l.552 */
#define RREC_CH_OFF_FRAMES            32u         /* FW l.554 */
#define RREC_CH_OFF_PAYLOAD_BYTES     36u         /* FW l.555 */
#define RREC_CH_OFF_FIRST_FRAME_INDEX 40u         /* FW l.556 */
#define RREC_CH_OFF_UTC_MS            48u         /* FW l.557 */
#define RREC_CH_OFF_UPTIME_NS         56u         /* FW l.558 */
#define RREC_CH_OFF_PDM_CLOCK_HZ      68u         /* FW l.560 */
#define RREC_CH_OFF_PDM_RATIO         72u         /* FW l.561 */
#define RREC_CH_OFF_GAIN_CODE         74u         /* FW l.562 */
#define RREC_CH_OFF_HIGHLIGHT_COUNT   76u         /* FW l.564 */
#define RREC_CH_OFF_HIGHLIGHT_FRAME   80u         /* FW l.566: 8 x u32 */
#define RREC_CH_OFF_BATTERY_MV        112u        /* FW l.567 */
#define RREC_CH_OFF_TEMP_C_X10        114u        /* FW l.568 */
#define RREC_CH_OFF_BOOT_COUNT        116u        /* FW l.569 */
#define RREC_CH_OFF_DROPOUT_BLOCKS    120u        /* FW l.570 */
#define RREC_CH_OFF_FW_VERSION        124u        /* FW l.571 */
#define RREC_CH_OFF_CYCLE_HZ          132u        /* FW l.573 */
#define RREC_CH_OFF_MOTOR_COUNT       144u        /* FW l.576 */
#define RREC_CH_OFF_MOTOR_FRAMES      148u        /* FW l.577: 4 x (start u32, end u32 exclusive) */
#define RREC_CH_OFF_PAYLOAD_CRC       504u        /* FW l.579 */
#define RREC_CH_OFF_HEADER_CRC        508u        /* FW l.580: CRC over header bytes 0 to 507 */
#define RREC_CH_FLAG_FIRST            (1u << 0)   /* FW l.547 */
#define RREC_CH_FLAG_LAST             (1u << 1)   /* FW l.547 */
/* bit 2 reserved, 0 (FW l.547) */
#define RREC_CH_FLAG_MOTOR            (1u << 3)   /* FW l.547 */
#define RREC_CH_FLAG_CLIPPED          (1u << 4)   /* FW l.547: a sample at -32768 or 32767 */
#define RREC_CH_FLAG_TIME_NOT_SET     (1u << 5)   /* FW l.547, l.1005 */
#define RREC_CH_FLAG_B15              (1u << 6)   /* FW l.547 */
#define RREC_CH_FLAG_DROPOUT          (1u << 7)   /* FW l.547, l.430 */
#define RREC_REC_TYPE_RECORDING       1u          /* FW l.548 */
#define RREC_REC_TYPE_FACTORY         2u          /* FW l.548, l.1024 */
#define RREC_SAMPLE_FORMAT_S16LE      1u          /* FW l.551 */
#define RREC_MIC_MASK                 0x03u       /* FW l.552 */
#define RREC_HIGHLIGHTS_PER_CHUNK     8u          /* FW l.564, l.566 (ruling D4: a ninth stays out of the chunk) */
#define RREC_MOTOR_PER_CHUNK          4u          /* FW l.576: a fifth is merged into the fourth */
#define RREC_UNUSED_U32               0xFFFFFFFFu /* FW l.566, l.577, l.632: unused highlight and motor slots */

/* ------------------------------------------------------------------ superblock, FW 5.4 */
#define RREC_SB_MAGIC                 0x42535252u /* "RRSB", FW l.591 */
#define RREC_SB_VERSION               1u          /* FW l.592 */
#define RREC_SB_OFF_MAGIC             0u          /* FW l.591 */
#define RREC_SB_OFF_VERSION           4u          /* FW l.592 */
#define RREC_SB_OFF_SIZE              6u          /* FW l.593 */
#define RREC_SB_OFF_SB_SEQ            8u          /* FW l.594 */
#define RREC_SB_OFF_CARD_SECTORS      12u         /* FW l.595 */
#define RREC_SB_OFF_CHUNK_FIRST_LBA   16u         /* FW l.596 */
#define RREC_SB_OFF_CHUNK_COUNT_TOTAL 20u         /* FW l.597 */
#define RREC_SB_OFF_HEAD_CHUNK_SEQ    24u         /* FW l.598 */
#define RREC_SB_OFF_TAIL_CHUNK_SEQ    28u         /* FW l.599 */
#define RREC_SB_OFF_NEXT_RECORDING_ID 32u         /* FW l.600 */
#define RREC_SB_OFF_INDEX_HEAD        36u         /* FW l.601 */
#define RREC_SB_OFF_INDEX_TAIL        40u         /* FW l.602 */
#define RREC_SB_OFF_OPEN_FLAG         44u         /* FW l.603 */
#define RREC_SB_OFF_OPEN_RECORDING_ID 48u         /* FW l.605 */
#define RREC_SB_OFF_OPEN_FIRST_CHUNK  52u         /* FW l.606 */
#define RREC_SB_OFF_BOOT_COUNT        56u         /* FW l.607 */
#define RREC_SB_OFF_LOG_HEAD          60u         /* FW l.608 */
#define RREC_SB_OFF_CRC               508u        /* FW l.610 */

/* ------------------------------------------------------------------ index records, FW 5.4 */
#define RREC_IX_MAGIC                 0x58495252u /* "RRIX", FW l.616 */
#define RREC_IX_VERSION               1u          /* FW l.617 */
#define RREC_IX_TYPE_CLOSE            1u          /* FW l.618 */
#define RREC_IX_TYPE_CONFIRM          2u          /* FW l.618 */
#define RREC_IX_TYPE_DELETE           3u          /* FW l.618 */
#define RREC_IX_CLOSE_COMPLETE        1u          /* FW l.619 */
#define RREC_IX_CLOSE_RECOVERED       2u          /* FW l.619 */
#define RREC_IX_OFF_MAGIC             0u          /* FW l.616 */
#define RREC_IX_OFF_VERSION           4u          /* FW l.617 */
#define RREC_IX_OFF_TYPE              6u          /* FW l.618 */
#define RREC_IX_OFF_CLOSE_STATE       7u          /* FW l.619 */
#define RREC_IX_OFF_RECORD_NUMBER     8u          /* FW l.620 */
#define RREC_IX_OFF_RECORDING_ID      12u         /* FW l.621 */
#define RREC_IX_OFF_FIRST_CHUNK_SEQ   16u         /* FW l.622 */
#define RREC_IX_OFF_CHUNK_COUNT       20u         /* FW l.623 */
#define RREC_IX_OFF_RECORDING_TYPE    24u         /* FW l.624 */
#define RREC_IX_OFF_CHANNELS          25u         /* FW l.625 */
#define RREC_IX_OFF_HIGHLIGHT_COUNT   26u         /* FW l.626 */
#define RREC_IX_OFF_SAMPLE_RATE       28u         /* FW l.627 */
#define RREC_IX_OFF_START_UTC_MS      32u         /* FW l.628 */
#define RREC_IX_OFF_DURATION_FRAMES   40u         /* FW l.629 */
#define RREC_IX_OFF_DIGEST            48u         /* FW l.630 */
#define RREC_IX_OFF_HIGHLIGHT_MS      56u         /* FW l.632: 32 x u32 */
#define RREC_IX_OFF_CRC               508u        /* FW l.634 */
#define RREC_CLOSE_HIGHLIGHTS         32u         /* FW l.582, l.632 */

/* ------------------------------------------------------------------ write strategy and space, FW 5.5, 5.6, 1.2 */
#define RREC_WRITE_TRIES              3u          /* FW l.643: 1 + 2 retries */
#define RREC_INIT_TRIES               3u          /* FW l.138 */
#define RREC_INIT_GAP_MS              200u        /* FW l.138 */
#define RREC_SD_RAIL_WAIT_MS          1u          /* FW l.506: wait 1 ms after VDD_SD on */
#define RREC_SFULL_CHUNKS             16u         /* FW l.651: SFULL at or under 16 free chunks */
#define RREC_S30_CHUNKS               3516u       /* FW l.652: S30 at or under 3,516 free chunks */
#define RREC_STORAGE_RETRY_MS         60000u      /* FW l.191 */
#define RREC_LIST_CACHE               256u        /* FW l.485 (ruling D16: the 256 newest) */

/* ------------------------------------------------------------------ USB, FW 6.1 */
#define RREC_USB_CLASS                0xFFu       /* FW l.669 */
#define RREC_USB_SUBCLASS             0x00u       /* FW l.669 */
#define RREC_USB_PROTOCOL             0x00u       /* FW l.669 */
#define RREC_USB_EP_OUT               0x01u       /* FW l.669 */
#define RREC_USB_EP_IN                0x81u       /* FW l.669 */
#define RREC_USB_MPS_FS               64u         /* FW l.669 */
#define RREC_USB_MPS_HS               512u        /* FW l.669 */

/* ------------------------------------------------------------------ USB messages, FW 6.2 */
#define RREC_MSG_MAGIC                0x5252u     /* FW l.681 */
#define RREC_MSG_HEADER_BYTES         16u         /* FW l.677 */
#define RREC_MSG_OFF_MAGIC            0u          /* FW l.681 */
#define RREC_MSG_OFF_OPCODE           2u          /* FW l.682 */
#define RREC_MSG_OFF_STATUS           3u          /* FW l.683 */
#define RREC_MSG_OFF_TAG              4u          /* FW l.684 */
#define RREC_MSG_OFF_LENGTH           8u          /* FW l.685 */
#define RREC_MSG_OFF_CRC              12u         /* FW l.686: 0 when length is 0 */

enum rrec_status {                                /* FW l.689 */
	RREC_ST_OK = 0,
	RREC_ST_BAD_MAGIC = 1,
	RREC_ST_BAD_CRC = 2,
	RREC_ST_UNKNOWN_OPCODE = 3,
	RREC_ST_BAD_ARG = 4,
	RREC_ST_NOT_FOUND = 5,
	RREC_ST_NOT_CONFIRMED = 6,
	RREC_ST_BUSY = 7,
	RREC_ST_STORAGE_ERROR = 8,
	RREC_ST_DIGEST_MISMATCH = 9,
	RREC_ST_FW_ERROR = 10,
	RREC_ST_NOT_ALLOWED = 11,             /* also FW_BEGIN when the update is not allowed (ruling D12) */
};

enum rrec_opcode {                                /* FW l.696 to l.708 */
	RREC_OP_GET_INFO = 0x01,
	RREC_OP_LIST_RECORDINGS = 0x02,
	RREC_OP_READ_RANGE = 0x03,
	RREC_OP_CONFIRM = 0x04,
	RREC_OP_DELETE = 0x05,
	RREC_OP_SET_TIME = 0x06,
	RREC_OP_GET_BATTERY = 0x07,
	RREC_OP_FW_BEGIN = 0x08,
	RREC_OP_FW_DATA = 0x09,
	RREC_OP_FW_END = 0x0A,
	RREC_OP_GET_LOG = 0x0B,
	RREC_OP_REBOOT = 0x0C,
	RREC_OP_FACTORY = 0x0D,
};
#define RREC_OP_FIRST                 0x01u
#define RREC_OP_LAST                  0x0Du

/* ------------------------------------------------------------------ USB commands, FW 6.3 (payload sizes and limits) */
#define RREC_PROTOCOL_VERSION         1u          /* FW l.696 */
#define RREC_GET_INFO_BYTES           35u         /* FW l.696 */
#define RREC_GI_OFF_PROTOCOL          0u          /* FW l.696, in the stated order */
#define RREC_GI_OFF_FW_VERSION        2u
#define RREC_GI_OFF_DEVICE_ID         6u
#define RREC_GI_OFF_CARD_SECTORS      14u
#define RREC_GI_OFF_CHUNK_COUNT_TOTAL 18u
#define RREC_GI_OFF_FREE_CHUNKS       22u
#define RREC_GI_OFF_RECORDINGS        26u
#define RREC_GI_OFF_BOOT_COUNT        30u
#define RREC_GI_OFF_FACTORY_FLAG      34u
#define RREC_LIST_REQ_BYTES           6u          /* FW l.697: first u32, max u16 */
#define RREC_LIST_MAX_MIN             1u          /* FW l.697 */
#define RREC_LIST_MAX_MAX             64u         /* FW l.697 */
#define RREC_LIST_ENTRY_BYTES         64u         /* FW l.697 */
#define RREC_LE_OFF_RECORDING_ID      0u          /* FW l.697, in the stated order */
#define RREC_LE_OFF_TYPE              4u
#define RREC_LE_OFF_CHANNELS          5u
#define RREC_LE_OFF_STATE             6u
#define RREC_LE_OFF_FIRST_CHUNK_SEQ   8u
#define RREC_LE_OFF_CHUNK_COUNT       12u
#define RREC_LE_OFF_SAMPLE_RATE       16u
#define RREC_LE_OFF_START_UTC_MS      20u
#define RREC_LE_OFF_DURATION_FRAMES   28u
#define RREC_LE_OFF_DIGEST            36u
#define RREC_LE_OFF_HIGHLIGHT_COUNT   40u
#define RREC_LIST_STATE_NEW           1u          /* FW l.697 */
#define RREC_LIST_STATE_TRANSFERRED   2u          /* FW l.697 */
#define RREC_LIST_STATE_RECOVERED     3u          /* FW l.697 */
#define RREC_READ_REQ_BYTES           12u         /* FW l.698 */
#define RREC_READ_COUNT_MIN           1u          /* FW l.698 */
#define RREC_READ_COUNT_MAX           256u        /* FW l.698 */
#define RREC_CONFIRM_REQ_BYTES        8u          /* FW l.699 */
#define RREC_DELETE_REQ_BYTES         4u          /* FW l.700 */
#define RREC_DELETE_RESP_BYTES        4u          /* FW l.700 */
#define RREC_SET_TIME_REQ_BYTES       10u         /* FW l.701: utc_ms i64, tz_offset_min i16 */
#define RREC_GET_BATTERY_BYTES        9u          /* FW l.702: u16 + u16 + u8 + i16 + u16 */
enum rrec_charge_state {                          /* FW l.702, GET_BATTERY "charging state" */
	RREC_CHG_OFF = 0,
	RREC_CHG_TRICKLE = 1,
	RREC_CHG_CC = 2,
	RREC_CHG_CV = 3,
	RREC_CHG_FULL = 4,
	RREC_CHG_ERROR = 5,
};
#define RREC_FW_BEGIN_REQ_BYTES       8u          /* FW l.703 */
#define RREC_FW_DATA_MIN              1u          /* FW l.704 */
#define RREC_FW_DATA_MAX              4096u       /* FW l.704, l.1013 */
#define RREC_GET_LOG_REQ_BYTES        6u          /* FW l.706 */
#define RREC_GET_LOG_MAX_MIN          1u          /* FW l.706 */
#define RREC_GET_LOG_MAX_MAX          32u         /* FW l.706 */

/* ------------------------------------------------------------------ battery and power, FW 1.1, 8 */
#define RREC_B15_SOC_X10              150u        /* FW l.115: at or under 15 % */
#define RREC_B5_SOC_X10               50u         /* FW l.116: at or under 5 % */
#define RREC_B5_MV                    3450u       /* FW l.116: or mean voltage at or under 3.45 V */
#define RREC_B2_SOC_X10               20u         /* FW l.117: at or under 2 % */
#define RREC_B2_MV                    3300u       /* FW l.117: or at or under 3.30 V */
#define RREC_MEAN_SAMPLES             10u         /* FW l.114, l.928: mean of the last 10 in the recording states */
#define RREC_SAMPLE_REC_MS            1000u       /* FW l.928 */
#define RREC_SAMPLE_IDLE_MS           60000u      /* FW l.928 */
#define RREC_SHPHLD_MS                96u         /* FW l.867, l.938 */
#define RREC_SHIP_RETRY_MS            1000u       /* FW l.941: still running 1 s after the ship task: log, retry once */
#define RREC_ILIM_SCREEN_MS           10000u      /* FW l.992 */
/* nPM1304 RSTCAUSE bits (FW l.996; [NPM p146], design/datasheets/npm1304_datasheet_v1_0.txt lines 12801 to 12888) */
#define RREC_RST_SHIPMODEEXIT         (1u << 0)
#define RREC_RST_BOOTMONITORTIMEOUT   (1u << 1)
#define RREC_RST_WATCHDOGTIMEOUT      (1u << 2)
#define RREC_RST_LONGPRESSTIMEOUT     (1u << 3)
#define RREC_RST_THERMALSHUTDOWN      (1u << 4)
#define RREC_RST_VSYSLOW              (1u << 5)
#define RREC_RST_SWRESET              (1u << 6)

/* ------------------------------------------------------------------ motor, FW 3.1 */
enum rrec_pattern {                               /* FW l.320 to l.328 */
	RREC_PAT_M1 = 1,                      /* 80 on */
	RREC_PAT_M2 = 2,                      /* 80 on, 120 off, 80 on */
	RREC_PAT_M3 = 3,                      /* 80 on, 120 off, 80 on, 120 off, 80 on */
	RREC_PAT_MH = 4,                      /* 40 on */
	RREC_PAT_MT = 5,                      /* 25 on */
	RREC_PAT_MW = 6,                      /* 60 on */
	RREC_PAT_MF = 7,                      /* 300 on, 200 off, 300 on */
};
#define RREC_PAT_COUNT                7u
#define RREC_MOTOR_RUN_MA             80u         /* FW l.332: charge per pulse t_on x 80 mA */
#define RREC_MOTOR_START_MA           175u        /* FW l.332: + 10 ms x 175 mA per pulse */
#define RREC_MOTOR_START_MS           10u         /* FW l.332 */

/* ------------------------------------------------------------------ update and flash layout, FW 9.2 */
#define RREC_FLASH_MCUBOOT_ADDR       0x00000000u /* FW l.1010 */
#define RREC_FLASH_MCUBOOT_BYTES      (64u * 1024u)
#define RREC_FLASH_SLOT0_ADDR         0x00010000u /* FW l.1010 */
#define RREC_FLASH_SLOT1_ADDR         0x00104000u /* FW l.1010, l.1012 */
#define RREC_FLASH_SLOT_BYTES         (976u * 1024u)  /* FW l.1010 */
#define RREC_FLASH_SETTINGS_ADDR      0x001F8000u /* FW l.1010 */
#define RREC_FLASH_SETTINGS_BYTES     (20u * 1024u)
#define RREC_FLASH_TOTAL_BYTES        (2036u * 1024u) /* FW l.1010 */
#define RREC_IMAGE_MAX_BYTES          999424u     /* FW l.1012: 976 KB */
#define RREC_SELFTEST_MS              30000u      /* FW l.1014 */
#define RREC_UPDATE_MIN_SOC_X10       300u        /* FW l.1015: allowed only ABOVE 30 % (or VBUS) */

/* ------------------------------------------------------------------ factory, FW 9.3 */
enum rrec_factory_sub {                           /* FW l.1019, l.1024 to l.1037 */
	RREC_FAC_ENTER = 0x01,                /* FW l.1019 */
	RREC_FAC_EXIT = 0x02,                 /* NOT IN FW: row FW l.201 names "FACTORY_EXIT" but FW 9.3 gives it no
	                                       * sub-command number; 0x02 is U0's proposal for the lead to rule */
	RREC_FAC_MIC = 0x10,                  /* T-MIC1/T-MIC2, argument 1 or 2 */
	RREC_FAC_SKEW_REMOVED = 0x11,         /* removed in F3: answers BAD_ARG (FW l.1037) */
	RREC_FAC_SCREEN = 0x20,
	RREC_FAC_JOY = 0x30,
	RREC_FAC_CENTRE = 0x31,
	RREC_FAC_MOTOR = 0x40,
	RREC_FAC_SIGN = 0x41,
	RREC_FAC_STORE = 0x50,
	RREC_FAC_RADIO = 0x60,
	RREC_FAC_CHARGE = 0x70,
	RREC_FAC_XTAL = 0x71,
	RREC_FAC_SHIP_SAMPLE = 0x7E,
	RREC_FAC_SHIP_ENTER = 0x7F,
};
#define RREC_FAC_RESULT_PASS          0u          /* FW l.1020 */
#define RREC_FAC_RESULT_FAIL          1u
#define RREC_FAC_RESULT_TIMEOUT       2u
#define RREC_FAC_MIC_REC_MS           2000u       /* FW l.1024 */
#define RREC_FAC_MIC_STUCK_RUN        1000u       /* FW l.1024: a run of 1,000 equal samples = stuck */
#define RREC_FAC_MOTOR_ON_MS          500u        /* FW l.1028 */
#define RREC_FAC_MOTOR_READ_MS        250u        /* FW l.1028 */
#define RREC_FAC_SIGN_REC_MS          1000u       /* FW l.1029 */
#define RREC_FAC_SIGN_GAP_MS          1000u       /* FW l.1029 */
#define RREC_FAC_RADIO_MS             10000u      /* FW l.1031 */
#define RREC_FAC_XTAL_MS              10000u      /* FW l.1033 */
#define RREC_ADV_INTERVAL_MS          100u        /* FW l.1031 (T-RADIO), l.1057 (ship beacon) */
#define RREC_ADV_TX_DBM               0           /* FW l.1031, l.1057 */
#define RREC_BEACON_NAME_PREFIX       "Ring"      /* FW l.1057: "Ring" + last 4 hex digits of the device id */
#define RREC_BEACON_NAME_LEN          8u          /* "Ring" + 4 hex digits, no terminator counted */

/* ------------------------------------------------------------------ event log and crash, FW 9.4 */
#define RREC_LOG_MAGIC                0x474C5252u /* "RRLG", FW l.1062 */
#define RREC_LOG_RECORD_BYTES         512u        /* FW l.1062 */
#define RREC_LOG_BUFFER_RECORDS       8u          /* FW l.1062: 4 KB RAM buffer */
#define RREC_LOG_ARG_BYTES            16u         /* FW l.1062 */
#define RREC_LG_OFF_MAGIC             0u          /* FW l.1062, in the stated order */
#define RREC_LG_OFF_SEQ               4u
#define RREC_LG_OFF_UPTIME_NS         8u
#define RREC_LG_OFF_UTC_MS            16u
#define RREC_LG_OFF_CODE              24u
#define RREC_LG_OFF_STATE             26u
#define RREC_LG_OFF_ARGS              28u
#define RREC_LG_OFF_CRASH             44u         /* crash block, zero when not a crash */
#define RREC_LG_OFF_CRC               508u        /* "CRC-32 in the last 4 bytes", over bytes 0 to 507 */
/* crash block (FW l.1063): reason u32, PC u32, LR u32, PSR u32, thread name 16 bytes, 64 stack words */
#define RREC_CRASH_STACK_WORDS        64u
#define RREC_CRASH_NAME_BYTES         16u
#define RREC_CRASH_BLOCK_BYTES        288u        /* 4 x 4 + 16 + 64 x 4 */
#define RREC_RETAINED_BYTES           1024u       /* FW l.1063, l.483 */
#define RREC_WDT_TIMEOUT_MS           8000u       /* FW l.1065 */
#define RREC_WDT_FEED_MS              1000u       /* FW l.1065 */
#define RREC_WDT_PROGRESS_MS          2000u       /* FW l.1065 */

/*
 * ================================================================== EVENT LOG CODES (decision D13)
 * FOR THE LEAD TO COPY INTO design/firmware.md section 9.4. FW names the record (l.1062) but no code list; these
 * codes are U0's, ruled "as used" (D13). code = u16 at RREC_LG_OFF_CODE; state = enum rc_state of the core at the
 * time; the 16 argument bytes are little-endian, unused bytes 0. "t_ms" = ms of the event's own time (GRTC uptime).
 */
enum rrec_log_code {
	RREC_LOG_STATE_CHANGE = 0x0001,       /* each state change, FW l.1062. args: from u8, to u8, row u16 (FW 1.2 row
	                                       * number of the core's table), event u8 (enum rc_event) */
	RREC_LOG_REC_START = 0x0002,          /* recording opened. args: recording_id u32, press t_ms i64 (FW l.448) */
	RREC_LOG_REC_STOP_PRESS = 0x0003,     /* stop press start time (FW l.448). args: recording_id u32, press start t_ms i64 */
	RREC_LOG_ZONE_UNKNOWN = 0x0004,       /* recording started with the zone unknown (FW l.1004; ruling D8). args: recording_id u32 */
	RREC_LOG_SIGN_REFUSED = 0x0005,       /* row FW l.148: sign not drawn. args: rscr_sign_start() answer i32 */
	RREC_LOG_FAULT_STORAGE_INIT = 0x0010, /* storage init failed 3 times (FW l.138). args: last errno i32 */
	RREC_LOG_FAULT_CHUNK_WRITE = 0x0011,  /* chunk write failed 3 times (FW l.168). args: chunk_seq u32, errno i32 */
	RREC_LOG_FAULT_MIC = 0x0012,          /* no PDM block for 100 ms (FW l.169). args: blocks so far u32 */
	RREC_LOG_FAULT_CHARGER = 0x0013,      /* charge error (FW l.176). args: BCHGERRREASON u8, BCHGERRSENSOR u8 */
	RREC_LOG_FAULT_SCAN_READ = 0x0014,    /* read error during the recovery scan (FW l.143). args: lba u32, errno i32 */
	RREC_LOG_STORAGE_RETRY = 0x0015,      /* 60 s retry result (FW l.191). args: result i32 (0 = success) */
	RREC_LOG_DROPOUT = 0x0016,            /* a PDM block replaced by zeros (FW l.430). args: recording_id u32,
	                                       * chunk_in_recording u32, block index in the chunk u8 */
	RREC_LOG_BATTERY = 0x0020,            /* a battery threshold reached, either way (FW l.1062). args: level u8
	                                       * (enum rc_batt), soc_x10 u16, mean mv u16 */
	RREC_LOG_STORAGE_S30 = 0x0021,        /* free space reached S30. args: free chunks u32 */
	RREC_LOG_STORAGE_SFULL = 0x0022,      /* free space reached SFULL. args: free chunks u32 */
	RREC_LOG_XFER_BASE = 0x0100,          /* a transfer command: code = 0x0100 | opcode (0x0101 to 0x010D), FW l.1062.
	                                       * args: status u8, tag u32, request length u32, first u32 argument */
	RREC_LOG_MOTOR_PATTERN = 0x0200,      /* pattern started (FW l.333). args: pattern u8 (enum rrec_pattern), t_ms i64 */
	RREC_LOG_ILIM_ACTIVE = 0x0210,        /* battery current limit active (FW l.991, l.995). args: battery_mv u16,
	                                       * state u8, screen on u8, count u32 */
	RREC_LOG_PMIC_RESET = 0x0220,         /* nPM1304 RSTCAUSE and charger error log at boot (FW l.996). args:
	                                       * RSTCAUSE u8, CHARGERERRREASON u8, CHARGERERRSENSOR u8 */
	RREC_LOG_MAIN_RESET = 0x0221,         /* the main chip's reset reason beside it (FW l.996). args: reason u32,
	                                       * gpregret1 u8 */
	RREC_LOG_CRASH = 0x0230,              /* a crash block copied at boot (FW l.1063); crash block filled */
	RREC_LOG_RECOVERY_DONE = 0x0240,      /* RECOVERY closed a recording (FW l.646). args: recording_id u32,
	                                       * chunks kept u32, head_chunk_seq u32 */
	RREC_LOG_SHIP_RETRY = 0x0250,         /* still running 1 s after the ship task (FW l.941). args: try u8 */
	RREC_LOG_TIME_GUESS = 0x0260,         /* the saved time at boot, used as a guess only (FW l.1005; ruling D18).
	                                       * args: saved utc_ms i64 */
	RREC_LOG_SELFTEST = 0x0270,           /* update self-test end (FW l.1014). args: result u8 (0 pass, 1 fail,
	                                       * 2 timeout), items passed mask u8 (bit 0 storage, 1 Bluetooth, 2 USB) */
	RREC_LOG_DROPPED = 0x0280,            /* records dropped from the full RAM buffer (FW l.1062). args: count u32 */
};

/* ------------------------------------------------------------------ shared types (used by several units) */
/* A log record before it is encoded (ring_store encodes it; FW l.1062). seq is set by ring_store. */
struct rrec_crash {
	uint32_t reason;
	uint32_t pc;
	uint32_t lr;
	uint32_t psr;
	char thread[RREC_CRASH_NAME_BYTES];
	uint32_t stack[RREC_CRASH_STACK_WORDS];
};
struct rrec_logrec {
	uint32_t seq;          /* set by ring_store when the record is queued */
	int64_t uptime_ns;     /* set by the caller (rhw clock) */
	int64_t utc_ms;        /* set by the caller; 0 when the time is not set */
	uint16_t code;         /* enum rrec_log_code */
	uint8_t state;         /* enum rc_state */
	uint8_t args[RREC_LOG_ARG_BYTES];
	bool has_crash;        /* false: the crash block is written as zeros */
	struct rrec_crash crash;
};
/* The log hook every unit receives from the join at start: queue one record; never blocks; any thread; not from an
 * interrupt handler. code/state/args as above; the hook fills seq, uptime_ns and utc_ms. */
typedef void (*rrec_log_fn)(uint16_t code, const uint8_t *args, size_t nargs);

#ifdef __cplusplus
}
#endif

#endif
