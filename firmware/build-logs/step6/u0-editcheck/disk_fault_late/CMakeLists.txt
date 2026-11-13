# Ring recorder driver interfaces (rhw): the active driver of each kind, the real clock, and the simulated drivers
# (CONFIG_RING_RHW_SIM). Software step 6, unit U0.
if(CONFIG_RING_RHW)
  zephyr_library_named(ring_rhw)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rhw.c src/rhw_clock_real.c)
  zephyr_library_sources_ifdef(CONFIG_RING_RHW_SIM
    src/sim_core.c
    src/sim_disk.c
    src/sim_mic.c
    src/sim_pmic.c
    src/sim_hfxo.c
    src/sim_misc.c
    src/sim_usb.c
    src/sim_image.c
  )
endif()
