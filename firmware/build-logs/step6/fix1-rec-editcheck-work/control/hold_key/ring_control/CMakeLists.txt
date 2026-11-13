# Ring control: report map, report builder and mode tables (pure logic, no radio),
# and the HID over GATT glue.
if(CONFIG_RING_CONTROL_LOGIC OR CONFIG_RING_CONTROL)
  zephyr_library_named(ring_control)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rctl_logic.c)
  zephyr_library_sources_ifdef(CONFIG_RING_CONTROL src/rctl.c)
endif()
