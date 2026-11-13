# Ring core: pure logic (state machine, gestures, dispatcher). No kernel, driver or Bluetooth calls.
if(CONFIG_RING_CORE)
  zephyr_library_named(ring_core)
  zephyr_library_sources(
    src/state_table.c
    src/state_actions.c
    src/gesture.c
    src/core.c
  )
  zephyr_include_directories(include)
endif()
