cd /ws/zephyr
echo ===dummy; cat drivers/display/display_dummy.c | head -150
echo ===dummy-dts; cat dts/bindings/display/zephyr,dummy-dc.yaml
echo ===lvgl.c; cat modules/lvgl/lvgl.c
echo ===lvgl_display; cat modules/lvgl/lvgl_display.c | head -150
echo ===Kconfig; grep -n "config LV_Z_\|config LVGL\|config LV_USE_OS\|config LV_Z_AUTO" -A3 modules/lvgl/Kconfig | head -150
