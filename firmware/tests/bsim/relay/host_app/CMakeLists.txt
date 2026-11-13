cmake_minimum_required(VERSION 3.20.0)

# The stand-in helper of the relay test: a Bluetooth central that pairs with the ring with the passkey (security level 4), finds the relay
# service, and writes frames to it like the Android helper app will. In scenario I it also serves a reduced Apple Notification Center Service
# (the stand-in iPhone) so that the ring finds that service on the link. Driven by a script in main.c.
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_relay_bsim_helper)

target_include_directories(app PRIVATE ../common)
target_sources(app PRIVATE src/main.c)
