# Ring factory (software step 6, unit U8): the pure part (rfa_logic.c) and the thin part (rfa.c, hardware only through
# ring_rhw's rhw.h and the other units' public headers). rfa_hw_real.c is the real beacon: development kit build only.
if(CONFIG_RING_FACTORY_LOGIC OR CONFIG_RING_FACTORY)
  zephyr_library_named(ring_factory)
  zephyr_include_directories(include)
  zephyr_library_include_directories(src)
  zephyr_library_sources(src/rfa_logic.c)
  zephyr_library_sources_ifdef(CONFIG_RING_FACTORY src/rfa.c)
  zephyr_library_sources_ifdef(CONFIG_RING_FACTORY_REAL src/rfa_hw_real.c)
endif()
