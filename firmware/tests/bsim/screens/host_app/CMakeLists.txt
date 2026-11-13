cmake_minimum_required(VERSION 3.20.0)

# The stand-in iPhone of the iPhone test: a Bluetooth central that pairs with the ring with the
# passkey (security level 4), acts as the HID host (the kit's HID over GATT client) and serves
# Apple's three services (Notification Center, Media, Current Time) from a GATT server whose
# services can be removed and added while linked. Driven by a script in main.c.
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_iphone_bsim_standin)

target_include_directories(app PRIVATE ../common)
target_sources(app PRIVATE src/main.c)
