cmake_minimum_required(VERSION 3.20.0)

# RING_RHW_DIR and RING_AUDIO_DIR let a run point at a broken copy of ring_rhw or ring_audio to prove that these tests
# can fail (broken_run.sh). RING_STORE_INCLUDE: the store's header folder (rau.h names the store's chunk type); a
# broken copy of ring_audio does not sit beside ring_store, so the path is given here.
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_AUDIO_DIR)
  set(RING_AUDIO_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_audio)
endif()
set(RING_STORE_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_store/include)
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_AUDIO_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_audio_tests)

# rau_chunk.h is the unit's own (not public) header of the pure part: taken from the same copy as the code.
target_include_directories(app PRIVATE ${RING_AUDIO_DIR}/src ${RING_STORE_INCLUDE} ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_sources(app PRIVATE
  src/common.c
  src/test_cfg.c
  src/test_chunk.c
  src/test_motor.c
  src/test_svc.c)
