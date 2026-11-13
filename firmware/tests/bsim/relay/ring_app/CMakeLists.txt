cmake_minimum_required(VERSION 3.20.0)

# The ring side of the relay test (the screens test's ring plus ring_relay): the real ring_devices, ring_control, ring_glue (which starts
# the iPhone part), ring_inbox, ring_time, ring_iphone, ring_relay, ring_screens and the core. RING_RELAY_DIR, RING_IPHONE_DIR and
# RING_INBOX_DIR let run.sh build a broken copy of a module (one named fault) to prove that a test can fail.
set(MOD ${CMAKE_CURRENT_SOURCE_DIR}/../../../../modules)
foreach(M IPHONE INBOX TIME SCREENS RELAY)
  string(TOLOWER ${M} ML)
  if(NOT DEFINED RING_${M}_DIR)
    set(RING_${M}_DIR ${MOD}/ring_${ML})
  endif()
endforeach()
list(APPEND ZEPHYR_EXTRA_MODULES ${MOD}/ring_core ${MOD}/ring_devices ${MOD}/ring_control ${MOD}/ring_glue
  ${RING_INBOX_DIR} ${RING_TIME_DIR} ${RING_IPHONE_DIR} ${RING_RELAY_DIR} ${RING_SCREENS_DIR})

# the link and stack settings are the product's: the same file (tools/build_all.sh, stage link-settings, compares the built settings)
if(NOT DEFINED RING_IPHONE_LINK_CONF)
  set(RING_IPHONE_LINK_CONF ${MOD}/ring_iphone/ring_iphone_link.conf)
endif()
list(APPEND EXTRA_CONF_FILE ${RING_IPHONE_LINK_CONF})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_relay_bsim_ring)

target_include_directories(app PRIVATE ../common)
target_sources(app PRIVATE src/main.c)
