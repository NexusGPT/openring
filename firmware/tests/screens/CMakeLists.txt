cmake_minimum_required(VERSION 3.20.0)

# The screens suite: the pure table (suite screens_table) and the drawing on the memory display (suite screens_draw).
# RING_SCREENS_DIR lets a run point at a broken copy of ring_screens to prove that these tests can fail:
# west twister ... --extra-args RING_SCREENS_DIR=<copy>
set(MOD ${CMAKE_CURRENT_SOURCE_DIR}/../../modules)
if(NOT DEFINED RING_SCREENS_DIR)
  set(RING_SCREENS_DIR ${MOD}/ring_screens)
endif()
# the header of the specification numbers (rrec_spec.h) the screens part takes the 10 s of the current limit from; a broken copy of
# ring_screens sits elsewhere and cannot find it by a relative path
set(RING_RHW_INCLUDE_DIR ${MOD}/ring_rhw/include)
list(APPEND ZEPHYR_EXTRA_MODULES ${MOD}/ring_core ${MOD}/ring_control ${MOD}/ring_devices ${MOD}/ring_inbox
  ${MOD}/ring_time ${MOD}/ring_iphone ${RING_SCREENS_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_screens_tests)

target_sources(app PRIVATE src/test_table.c src/test_draw.c)
