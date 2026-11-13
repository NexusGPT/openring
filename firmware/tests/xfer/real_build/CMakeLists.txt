cmake_minimum_required(VERSION 3.20.0)

# A build-only check that the real USB file of ring_xfer (rxf_hw_real.c) compiles and links against the kit's USB device
# stack with the simulated drivers OFF, as the development kit build has them. It is not run and proves nothing about a ring.
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../../modules/ring_rhw)
endif()
if(NOT DEFINED RING_XFER_DIR)
  set(RING_XFER_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../../modules/ring_xfer)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_XFER_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_xfer_real_build)

target_sources(app PRIVATE src/main.c)
