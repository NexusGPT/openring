cmake_minimum_required(VERSION 3.20.0)

# The modules are found by path, so this test builds without a west.yml entry.
# RING_CONTROL_DIR lets a run point at a broken copy of ring_control (one wrong key)
# to prove that these tests can fail: west twister ... --extra-args RING_CONTROL_DIR=<copy>
if(NOT DEFINED RING_CONTROL_DIR)
  set(RING_CONTROL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_control)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES
  ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_core
  ${RING_CONTROL_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_control_tests)

target_sources(app PRIVATE src/test_control.c)
