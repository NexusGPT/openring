cmake_minimum_required(VERSION 3.20.0)

# The module is found by path, so this test builds without a west.yml entry.
# RING_DEVICES_DIR lets a run point at a broken copy of ring_devices to prove that
# these tests can fail: west twister ... --extra-args RING_DEVICES_DIR=<copy>
if(NOT DEFINED RING_DEVICES_DIR)
  set(RING_DEVICES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_devices)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_DEVICES_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_devices_tests)

target_sources(app PRIVATE src/test_devices.c)
