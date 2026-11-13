# Ring inbox: the store of the last notifications (pure logic, no radio).
if(CONFIG_RING_INBOX)
  zephyr_library_named(ring_inbox)
  zephyr_include_directories(include)
  zephyr_library_sources(src/rinbox.c)
endif()
