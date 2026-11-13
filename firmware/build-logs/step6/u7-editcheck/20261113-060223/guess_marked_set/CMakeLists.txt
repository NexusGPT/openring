# Ring sys: the pure part (rsy_logic.c) and the thin part (rsy.c); the real driver file (rsy_hw_real.c) only when the
# simulated drivers are off (the development kit build). Software step 6, unit U7.
if(CONFIG_RING_SYS_LOGIC OR CONFIG_RING_SYS)
  zephyr_library_named(ring_sys)
  zephyr_include_directories(include)
  zephyr_library_include_directories(src)
  zephyr_library_sources(src/rsy_logic.c)
  zephyr_library_sources_ifdef(CONFIG_RING_SYS src/rsy.c)
  zephyr_library_sources_ifdef(CONFIG_RING_SYS_FATAL_HANDLER src/rsy_fatal.c)
  if(CONFIG_RING_SYS AND NOT CONFIG_RING_RHW_SIM)
    zephyr_library_sources(src/rsy_hw_real.c)
  endif()
endif()
