cmake_minimum_required(VERSION 3.20.0)

# RING_RELAY_DIR and RING_INBOX_DIR let a run point at a broken copy of ring_relay or ring_inbox to prove that these tests can fail.
if(NOT DEFINED RING_RELAY_DIR)
  set(RING_RELAY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_relay)
endif()
if(NOT DEFINED RING_INBOX_DIR)
  set(RING_INBOX_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_inbox)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_INBOX_DIR} ${RING_RELAY_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_relay_tests)

target_sources(app PRIVATE src/test_relay.c)
