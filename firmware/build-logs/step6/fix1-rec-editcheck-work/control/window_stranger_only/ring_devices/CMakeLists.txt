# Ring devices: device list and switch decision (pure logic, no radio), and
# the Bluetooth part (pairing, identities, advertising, switching).
if(CONFIG_RING_DEVICES_LOGIC OR CONFIG_RING_DEVICES)
  zephyr_library_named(ring_devices)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rdev_logic.c)
  zephyr_library_sources_ifdef(CONFIG_RING_DEVICES src/rdev.c)
endif()
