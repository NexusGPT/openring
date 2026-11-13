cmake_minimum_required(VERSION 3.20.0)

# RING_TIME_DIR lets a run point at a broken copy of ring_time to prove that these tests can fail.
if(NOT DEFINED RING_TIME_DIR)
  set(RING_TIME_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_time)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_TIME_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_time_tests)

target_sources(app PRIVATE src/test_time.c)
