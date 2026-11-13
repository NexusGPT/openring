U2 store: unit passes. RESULT: done.

Cited run: build-logs/step6/u2-final10.console. Last lines: l.1563 `RESULT PASS`, l.1565 `UNIT PASS tests/store`, l.1567 `# remote exit code: 0`. 63 of 63 cases on native_sim (l.22) and on the simulated chip (l.44). Per-case PASS lines of that run: build-logs/step6/u2-cases10.console.

Built (modules/ring_store/, tests/store/, docs/store-notes.md): rst_fmt.c, rst_layout.c, rst_log.c (pure), rst.c (thin), rst_hw_real.c (unproven, never compiled by a run), 9 suites, broken_edit.py, broken_run.sh.

Broken copies: all 11 fail their named case on both targets, and only cases on each copy's declared list fail with it (final10 console, `X on ... as required` lines, table in the notes). Four fail only their own case (hdr_crc_512, scan_accepts_gap, two_tries, init_before_rail).

Rows: S2 to S29, C3, C8, C9, C16, C24, T26 are mapped to case and log line in docs/store-notes.md; NP rows: S6 CMD25, S19, S25, S30, pin levels, real card. K12 true (test_crc_check_value). K2: names exist (compile test and grep counts in u2-k2-grep.log); argument types unchecked.

For the header (in the notes, section 5): rst_put_chunk -ENOSPC when a chunk would overwrite an unfreed one (also -EINVAL for bad frames, over 8 highlights or over 4 motor intervals; the store overwrites recording_id and recording_type); rst_delete -EBUSY when a recording is open or the open flag is set.

Flags for the lead: the pure files also call crc32_ieee_update (D11a names only crc32_ieee); a card with no valid superblock is formatted (question for the owner); ruling R24 applied in the recovery scan (frame x 1000 / 16000); the superblock is also written at CONFIRM, DELETE and recovery; "superblock never in flight with a chunk" holds by construction, no case of its own.

Audit: u2-audit.py checked 97 claims of the notes against the logs and sources, 0 failed (u2-audit.log). Searches: u2-search-*.log. Server folder /root/ring-os/src-u-store left in place (named in your brief); no process of mine runs (u2-cleanup.log).

Last line of docs/store-notes.md: RESULT: done, unit U2 passes on both simulated targets (63 of 63 cases, 11 of 11 broken copies fail their named case) in the cited run
