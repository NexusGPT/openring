cmake_minimum_required(VERSION 3.20.0)

# RING_RHW_DIR and RING_SYS_DIR let a run point at a broken copy of ring_rhw or ring_sys to prove that these tests can
# fail (broken_run.sh). ring_time (existing) is added because the saved-time test checks that the guess never reaches
# the clock.
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_SYS_DIR)
  set(RING_SYS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_sys)
endif()
set(RING_TIME_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_time)
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_SYS_DIR} ${RING_TIME_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_sys_tests)

# rsy_logic.h and rsy_int.h are the unit's own (not public) headers: taken from the same copy as the code.
target_include_directories(app PRIVATE ${RING_SYS_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_sources(app PRIVATE
  src/common.c
  src/test_update.c
  src/test_time.c
  src/test_persist.c
  src/test_crash.c
  src/test_wdt.c)
