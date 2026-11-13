cmake_minimum_required(VERSION 3.20.0)

# The ring side of the two-device tests: the real ring_devices, ring_control and ring_glue
# modules (the glue is the same module the product application runs), the core as the source of
# the joystick actions, and a test hook that injects joystick edges in simulated time.
# RING_CONTROL_DIR and RING_DEVICES_DIR let run.sh build a broken copy of a module (one named
# fault) to prove that a test can fail.
set(MOD ${CMAKE_CURRENT_SOURCE_DIR}/../../../../modules)
if(NOT DEFINED RING_CONTROL_DIR)
  set(RING_CONTROL_DIR ${MOD}/ring_control)
endif()
if(NOT DEFINED RING_DEVICES_DIR)
  set(RING_DEVICES_DIR ${MOD}/ring_devices)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${MOD}/ring_core ${RING_DEVICES_DIR} ${RING_CONTROL_DIR} ${MOD}/ring_glue)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_control_bsim_ring)

target_include_directories(app PRIVATE ../common)
target_sources(app PRIVATE src/main.c)
