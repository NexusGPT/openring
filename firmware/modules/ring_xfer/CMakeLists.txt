# Ring recorder USB transfer (software step 6, unit U4). The pure files (rxf_proto.c, rxf_desc.c) make no kernel call;
# rxf_class.c is the thin part (reaches hardware only through ring_rhw); the real-stack file (rxf_hw_real.c) is built
# only where the simulated drivers are off (the development kit build) and is not proven.
if(CONFIG_RING_XFER_LOGIC OR CONFIG_RING_XFER)
  zephyr_library_named(ring_xfer)
  zephyr_include_directories(include)
  zephyr_library_include_directories(src)
  zephyr_library_sources(src/rxf_proto.c src/rxf_desc.c)
  zephyr_library_sources_ifdef(CONFIG_RING_XFER src/rxf_class.c)
  if(CONFIG_RING_XFER AND NOT CONFIG_RING_RHW_SIM)
    zephyr_library_sources(src/rxf_hw_real.c)
  endif()
endif()
