# The ring (software step 7): flashed over SWD (test pads TP3, TP4, TP5) as the development kit is.
board_runner_args(jlink "--device=nRF54LM20A_M33" "--speed=4000")

include(${ZEPHYR_BASE}/boards/common/nrfutil.board.cmake)
include(${ZEPHYR_BASE}/boards/common/jlink.board.cmake)
