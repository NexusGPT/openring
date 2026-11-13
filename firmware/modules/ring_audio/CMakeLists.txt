# Ring audio: the pure part (rau_chunk.c) and the thin part (rau.c); the real driver file (rau_hw_real.c) only when the
# simulated drivers are off (the development kit build).
if(CONFIG_RING_AUDIO_LOGIC OR CONFIG_RING_AUDIO)
  zephyr_library_named(ring_audio)
  zephyr_include_directories(include)
  # rau.h names the store's chunk type (header only). A test that points RING_AUDIO_DIR at a broken copy sets
  # RING_STORE_INCLUDE, because the copy does not sit beside ring_store.
  if(NOT DEFINED RING_STORE_INCLUDE)
    set(RING_STORE_INCLUDE ${CMAKE_CURRENT_LIST_DIR}/../ring_store/include)
  endif()
  zephyr_include_directories(${RING_STORE_INCLUDE})
  zephyr_library_include_directories(src)
  zephyr_library_sources(src/rau_chunk.c)
  zephyr_library_sources_ifdef(CONFIG_RING_AUDIO src/rau.c)
  if(CONFIG_RING_AUDIO AND NOT CONFIG_RING_RHW_SIM)
    zephyr_library_sources(src/rau_hw_real.c)
  endif()
endif()
