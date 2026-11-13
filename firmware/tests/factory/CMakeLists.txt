cmake_minimum_required(VERSION 3.20.0)

# RING_FACTORY_DIR and RING_RHW_DIR let a run point at a broken copy of ring_factory or ring_rhw to prove that these
# tests can fail (broken_run.sh). The other units are the finished ones, used as they are.
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_FACTORY_DIR)
  set(RING_FACTORY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_factory)
endif()
set(RING_MODS ${CMAKE_CURRENT_SOURCE_DIR}/../../modules)
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_FACTORY_DIR} ${RING_MODS}/ring_core ${RING_MODS}/ring_store
     ${RING_MODS}/ring_audio ${RING_MODS}/ring_power ${RING_MODS}/ring_sys)

# the scenario ring_factory.screen (FACTORY_SCREEN=ON): the real screens part on the memory display, with the modules it needs
if(FACTORY_SCREEN)
  list(APPEND ZEPHYR_EXTRA_MODULES ${RING_MODS}/ring_screens ${RING_MODS}/ring_control ${RING_MODS}/ring_devices
       ${RING_MODS}/ring_inbox ${RING_MODS}/ring_time ${RING_MODS}/ring_iphone)
  list(APPEND EXTRA_CONF_FILE ${CMAKE_CURRENT_SOURCE_DIR}/screen.conf)
  if(BOARD MATCHES "native_sim")
    set(DTC_OVERLAY_FILE "${CMAKE_CURRENT_SOURCE_DIR}/app.overlay;${CMAKE_CURRENT_SOURCE_DIR}/screen_native_sim.overlay")
  else()
    set(DTC_OVERLAY_FILE "${CMAKE_CURRENT_SOURCE_DIR}/app.overlay;${CMAKE_CURRENT_SOURCE_DIR}/screen_bsim.overlay")
  endif()
endif()

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_factory_tests)

# rfa_logic.h is the unit's own (not public) header of the pure part: taken from the same copy as the code. rpw_priv.h is
# the power unit's test reset (tests of that unit use it the same way).
target_include_directories(app PRIVATE ${RING_FACTORY_DIR}/src ${RING_MODS}/ring_power/src ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_sources(app PRIVATE
  src/common.c
  src/test_cmd.c
  src/test_mic.c
  src/test_input.c
  src/test_motor.c
  src/test_sign.c
  src/test_store.c
  src/test_radio.c
  src/test_charge.c
  src/test_xtal.c
  src/test_ship.c
  src/test_screen.c)
