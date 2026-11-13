cmake_minimum_required(VERSION 3.20.0)

# Trial: the ring holds two devices at the same time (two links, two identities). Not the
# product: ring_devices' single-link plan is not used; this app only registers the HID service
# of ring_control and sends keys to each link with a test hook.
set(MOD ${CMAKE_CURRENT_SOURCE_DIR}/../../../../modules)
list(APPEND ZEPHYR_EXTRA_MODULES ${MOD}/ring_core ${MOD}/ring_devices ${MOD}/ring_control)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_control_bsim_trial)

target_include_directories(app PRIVATE ../common)
target_sources(app PRIVATE src/main.c)
