# Ring power (software step 6, unit U5): the pure part (rpw_logic.c) and the thin part (rpw.c, hardware only through
# ring_rhw's rhw.h). rpw_hw_real.c is the real driver file: development kit build only, not proven (plan section 7).
if(CONFIG_RING_POWER)
  zephyr_library_named(ring_power)
  zephyr_include_directories(include src)
  # ring_core's rc_types.h (pure header) names the states rpw_state() reads
  zephyr_include_directories(${CMAKE_CURRENT_LIST_DIR}/../ring_core/include)
  zephyr_library_sources(src/rpw_logic.c src/rpw.c)
  zephyr_library_sources_ifdef(CONFIG_RING_POWER_REAL src/rpw_hw_real.c)
endif()
