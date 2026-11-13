# Ring recorder storage (software step 6, unit U2). The pure files make no kernel call; rst.c is the thin part; the
# real-driver file is built only where the simulated drivers are off (development kit build) and is not proven.
if(CONFIG_RING_STORE)
  zephyr_library_named(ring_store)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rst_fmt.c src/rst_layout.c src/rst_log.c src/rst.c)
  zephyr_library_sources_ifndef(CONFIG_RING_RHW_SIM src/rst_hw_real.c)
endif()
