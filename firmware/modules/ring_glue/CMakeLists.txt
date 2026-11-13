# Ring glue: carries the joystick through the core to control and to recording.
if(CONFIG_RING_GLUE)
  zephyr_library_named(ring_glue)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rglue.c)
endif()
