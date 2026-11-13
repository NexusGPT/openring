cmake_minimum_required(VERSION 3.20.0)

# RING_XFER_DIR (and RING_RHW_DIR, RING_STORE_DIR) let a run point at a broken copy of ring_xfer to prove that these
# tests can fail (broken_run.sh).
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_STORE_DIR)
  set(RING_STORE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_store)
endif()
if(NOT DEFINED RING_XFER_DIR)
  set(RING_XFER_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_xfer)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_STORE_DIR} ${RING_XFER_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_xfer_tests)

# the pure files' own headers (not public) so the logic suites can call them directly
target_include_directories(app PRIVATE ${RING_XFER_DIR}/src)

target_sources(app PRIVATE
  src/xt.c src/glue.c
  src/test_proto.c src/test_desc.c src/test_svc.c src/test_store.c)
