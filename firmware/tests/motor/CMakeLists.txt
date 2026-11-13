cmake_minimum_required(VERSION 3.20.0)

# RING_RHW_DIR and RING_MOTOR_DIR let a run point at a broken copy of ring_rhw or ring_motor to prove that these tests
# can fail (broken_run.sh).
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_MOTOR_DIR)
  set(RING_MOTOR_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_motor)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_MOTOR_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_motor_tests)

# rmo_logic.h is the unit's own (not public) header of the pure part: taken from the same copy as the code.
target_include_directories(app PRIVATE ${RING_MOTOR_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_sources(app PRIVATE
  src/common.c
  src/test_player.c
  src/test_charge.c)
