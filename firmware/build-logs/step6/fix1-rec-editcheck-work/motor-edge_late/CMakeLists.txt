# Ring motor: the pure part (rmo_logic.c) and the thin part (rmo.c); the real driver file (rmo_hw_real.c) only when the
# simulated drivers are off (the development kit build).
if(CONFIG_RING_MOTOR_LOGIC OR CONFIG_RING_MOTOR)
  zephyr_library_named(ring_motor)
  zephyr_include_directories(include)
  zephyr_library_include_directories(src)
  zephyr_library_sources(src/rmo_logic.c)
  zephyr_library_sources_ifdef(CONFIG_RING_MOTOR src/rmo.c)
  if(CONFIG_RING_MOTOR AND NOT CONFIG_RING_RHW_SIM)
    zephyr_library_sources(src/rmo_hw_real.c)
  endif()
endif()
