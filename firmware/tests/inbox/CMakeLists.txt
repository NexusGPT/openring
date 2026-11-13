cmake_minimum_required(VERSION 3.20.0)

# RING_INBOX_DIR lets a run point at a broken copy of ring_inbox to prove that these tests can fail:
# west twister ... --extra-args RING_INBOX_DIR=<copy>
if(NOT DEFINED RING_INBOX_DIR)
  set(RING_INBOX_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_inbox)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_INBOX_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_inbox_tests)

target_sources(app PRIVATE src/test_inbox.c)
