# Ring relay: the pure part (frames, record parser, refusal decisions) and the Bluetooth part (the GATT service).
if(CONFIG_RING_RELAY_LOGIC OR CONFIG_RING_RELAY)
  zephyr_library_named(ring_relay)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rrl.c)
  zephyr_library_sources_ifdef(CONFIG_RING_RELAY src/rrl_bt.c)
endif()
