cmake_minimum_required(VERSION 3.20.0)

# RING_STORE_DIR (and RING_RHW_DIR) let a run point at a broken copy of ring_store (or ring_rhw) to prove that these
# tests can fail (broken_run.sh).
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_STORE_DIR)
  set(RING_STORE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_store)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_STORE_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_store_tests)

# the pure files' own headers (not public) so the logic suites can call them directly
target_include_directories(app PRIVATE ${RING_STORE_DIR}/src)

target_sources(app PRIVATE
  src/tst.c
  src/test_fmt.c src/test_layout.c src/test_log.c src/test_index.c src/test_space.c
  src/test_recovery.c src/test_delete.c src/test_evlog.c src/test_svc.c)
