cmake_minimum_required(VERSION 3.20.0)
# Compile check of ring_sys's real driver file against the kit for the nRF54LM20 development kit (manual, not part of
# the unit run: no testcase.yaml here). See ../../../docs/sys-notes.md.
set(FWM ${CMAKE_CURRENT_SOURCE_DIR}/../../../modules)
list(APPEND ZEPHYR_EXTRA_MODULES ${FWM}/ring_rhw ${FWM}/ring_sys)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_sys_kitcompile)
target_include_directories(app PRIVATE ${FWM}/ring_sys/src)
target_sources(app PRIVATE src/main.c)
