cmake_minimum_required(VERSION 3.20.0)

# The recorder's suites (software step 6, unit J): the real core, glue, screens and every unit of step 6 on the simulated
# drivers of ring_rhw. RING_RECORDER_DIR lets broken_run.sh point at a broken copy of ring_recorder to prove that these tests
# can fail: west twister ... --extra-args RING_RECORDER_DIR=<copy>
set(MOD ${CMAKE_CURRENT_SOURCE_DIR}/../../modules)
if(NOT DEFINED RING_RECORDER_DIR)
  set(RING_RECORDER_DIR ${MOD}/ring_recorder)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${MOD}/ring_rhw ${MOD}/ring_core ${MOD}/ring_control ${MOD}/ring_devices ${MOD}/ring_inbox
  ${MOD}/ring_time ${MOD}/ring_iphone ${MOD}/ring_glue ${MOD}/ring_screens ${MOD}/ring_store ${MOD}/ring_audio
  ${MOD}/ring_xfer ${MOD}/ring_power ${MOD}/ring_motor ${MOD}/ring_sys ${MOD}/ring_factory ${RING_RECORDER_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_recorder_tests)

target_include_directories(app PRIVATE src)
# RT_SUITE=<file> (without .c) builds the harness and that one suite file only: broken_run.sh uses it so that each broken
# copy runs the suite of its named case.
if(DEFINED RT_SUITE)
  target_sources(app PRIVATE src/rt.c src/${RT_SUITE}.c)
else()
target_sources(app PRIVATE
  src/rt.c
  src/test_rows.c
  src/test_actions.c
  src/test_boot.c
  src/test_sign.c
  src/test_sign1.c
  src/test_sequence.c
  src/test_rails.c
  src/test_rules.c
  src/test_log.c
  src/test_screens.c
  src/test_ship.c
  src/test_unmount.c
  src/test_factory.c
  src/test_noscreens.c)
endif()
