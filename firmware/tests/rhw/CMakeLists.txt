cmake_minimum_required(VERSION 3.20.0)

# RING_RHW_DIR lets a run point at a broken copy of ring_rhw to prove that these tests can fail (broken_run.sh).
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../modules/ring_rhw)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_rhw_tests)

# The public headers of the other units of step 6 (written by U0), compiled alone, one file per header; ring_core's
# include folder only for the core's types that rrec.h names (the core itself is not built here).
set(FWM ${CMAKE_CURRENT_SOURCE_DIR}/../../modules)
target_include_directories(app PRIVATE
  ${FWM}/ring_store/include ${FWM}/ring_audio/include ${FWM}/ring_xfer/include ${FWM}/ring_power/include
  ${FWM}/ring_motor/include ${FWM}/ring_sys/include ${FWM}/ring_factory/include ${FWM}/ring_recorder/include
  ${FWM}/ring_core/include)

target_sources(app PRIVATE
  src/test_rhw.c
  src/hdr_rrec_spec.c src/hdr_rhw.c src/hdr_rhw_sim.c
  src/hdr_rst.c src/hdr_rau.c src/hdr_rxf.c src/hdr_rpw.c src/hdr_rmo.c src/hdr_rsy.c src/hdr_rfa.c src/hdr_rrec.c)
