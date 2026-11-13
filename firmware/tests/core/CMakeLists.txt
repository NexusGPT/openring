cmake_minimum_required(VERSION 3.20.0)

# The ring core module is found by path, so this test builds without a west.yml entry.
# RING_CORE_DIR lets a run point at a broken copy of the module (broken_run.sh) to prove that these tests can fail.
if(NOT DEFINED RING_CORE_DIR)
  set(RING_CORE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_core)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_CORE_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_core_tests)

target_include_directories(app PRIVATE src)
target_sources(app PRIVATE
  src/th.c
  src/test_rows.c
  src/test_gesture.c
  src/test_rules.c
  src/test_round2.c
  src/test_round3.c
  src/test_round4.c
)
