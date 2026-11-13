Expected result of run 1 (written before it ended), `bash tools/unit_run.sh tests/rhw`:
- tests-native_sim: 1 of 1 configuration passed, every rhw_sim case PASS (42 cases in test_rhw.c; corrected from 45 after a count with grep -c, before the run ended).
- tests-nrf54lm20bsim_nrf54lm20a_cpuapp: the same; K15 case passes (pool 4096 sectors + 3 chunks fit).
- broken-rhw: 4 variants x 2 boards, each named case FAIL, RESULT PASS.
- last line `UNIT PASS tests/rhw`.
Risk named in advance: first compile of new code; timing asserts on the bsim board (32768 Hz ticks).
