# Ring recorder: the join of software step 6 (unit J). The public header include/ring_recorder/rrec.h is frozen (written by
# unit U0); src/rrec_int.h holds the join's two glue entries (after, screen fact) and the test read-outs.
if(CONFIG_RING_RECORDER)
  zephyr_library_named(ring_recorder)
  zephyr_include_directories(include src)
  zephyr_library_sources(
    src/rrec.c
    src/rrec_mics.c
    src/rrec_boot.c
    src/rrec_bridge.c
    src/rrec_backend.c
  )
endif()
