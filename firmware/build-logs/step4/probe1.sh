cd /ws
ls modules/lib | head -50
echo ---lvgl; ls modules/lib/gui 2>&1; ls modules/lib/gui/lvgl 2>&1 | head; grep -n "LVGL_VERSION_M" modules/lib/gui/lvgl/src/lv_version.h modules/lib/gui/lvgl/lv_version.h 2>&1 | head
echo ---zephyr display; ls zephyr/drivers/display | head -80
echo ---lvgl glue; ls zephyr/modules/lvgl; ls zephyr/boards/native/native_sim/*.dts zephyr/boards/native/nrf_bsim/ 2>&1| head -30
echo ---dts; grep -rn "display\|sdl" zephyr/boards/native/native_sim/native_sim.dts | head
echo ---nrf54lm20bsim; ls zephyr/boards/native/nrf_bsim | head -30
