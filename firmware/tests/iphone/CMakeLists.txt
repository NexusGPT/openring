cmake_minimum_required(VERSION 3.20.0)

# RING_IPHONE_DIR lets a run point at a broken copy of ring_iphone to prove that these tests can fail.
if(NOT DEFINED RING_IPHONE_DIR)
  set(RING_IPHONE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_iphone)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES
  ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_inbox
  ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_time
  ${RING_IPHONE_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_iphone_tests)

target_sources(app PRIVATE src/test_iphone.c)
