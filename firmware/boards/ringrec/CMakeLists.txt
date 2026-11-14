# The ring (software step 7). Zephyr adds a board folder's CMakeLists.txt to every image built for the board
# (zephyr/boards/CMakeLists.txt). It gives the build the board's own headers: include/rpw_battery_model.h, the cell
# model the power part's real file (modules/ring_power/src/rpw_hw_real.c) includes by that name.
zephyr_include_directories(include)
