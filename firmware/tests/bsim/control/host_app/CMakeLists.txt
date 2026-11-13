cmake_minimum_required(VERSION 3.20.0)

# The stand-in host of the two-device tests: a Bluetooth central with a HID host
# role (the SDK's HID over GATT client) that pairs with the passkey and
# subscribes to the reports.
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_control_bsim_host)

target_include_directories(app PRIVATE ../common)
target_sources(app PRIVATE src/main.c)
