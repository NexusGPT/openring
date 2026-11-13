# Ring time: the clock record (pure logic) and the kernel wrapper.
if(CONFIG_RING_TIME_LOGIC OR CONFIG_RING_TIME)
  zephyr_library_named(ring_time)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rtime_logic.c)
  zephyr_library_sources_ifdef(CONFIG_RING_TIME src/rtime.c)
endif()
