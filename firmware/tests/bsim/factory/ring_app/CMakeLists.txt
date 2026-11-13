cmake_minimum_required(VERSION 3.20.0)

# The ring side of the ship beacon test: the real factory part (ring_factory) with its real beacon (rfa_hw_real.c, the
# Bluetooth host) on the simulated ring chip. RING_FACTORY_DIR lets run.sh build a broken copy of the factory part to prove
# that the test can fail. Nothing of the other recorder units is in this application: the join's two steps that matter to
# the beacon (the factory flag, and the call that stops the beacon right before the ship task) are written in main.c.
set(MOD ${CMAKE_CURRENT_SOURCE_DIR}/../../../../modules)
if(NOT DEFINED RING_RHW_DIR)
  set(RING_RHW_DIR ${MOD}/ring_rhw)
endif()
if(NOT DEFINED RING_FACTORY_DIR)
  set(RING_FACTORY_DIR ${MOD}/ring_factory)
endif()
list(APPEND ZEPHYR_EXTRA_MODULES ${RING_RHW_DIR} ${RING_FACTORY_DIR})

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_factory_bsim_ring)

# rfa_logic.h is the unit's own (not public) header: the ring's name is printed with the same function the beacon uses
target_include_directories(app PRIVATE ${RING_FACTORY_DIR}/src)
target_sources(app PRIVATE src/main.c)
