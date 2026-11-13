# Ring iPhone part: the pure logic (ANCS reassembly, AMS decoder) and the Bluetooth part (the kit's
# notification, media, time and GATT service clients).
if(CONFIG_RING_IPHONE_LOGIC OR CONFIG_RING_IPHONE)
  zephyr_library_named(ring_iphone)
  zephyr_include_directories(include)
  zephyr_library_sources(src/ripl.c)
  zephyr_library_sources_ifdef(CONFIG_RING_IPHONE src/rip.c)
endif()
