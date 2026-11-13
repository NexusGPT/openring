# U7 kit facts K9, K10, K11: counts and file names only (no kit lines printed).
Z=/ws/zephyr
echo "== K9 names in dfu headers (count of lines mentioning each name; 0 = absent)"
for n in boot_request_upgrade boot_is_img_confirmed boot_write_img_confirmed BOOT_UPGRADE_TEST; do
  echo "mcuboot.h $n $(grep -c "$n" $Z/include/zephyr/dfu/mcuboot.h)"
done
for n in flash_img_init_id flash_img_buffered_write flash_img_check flash_img_init flash_img_bytes_written; do
  echo "flash_img.h $n $(grep -c "$n" $Z/include/zephyr/dfu/flash_img.h)"
done
echo "== K10 settings back ends (counts in the settings Kconfig; files holding retained / settings nodes)"
for n in SETTINGS_NVS SETTINGS_ZMS SETTINGS_FILE SETTINGS_FCB; do
  echo "subsys/settings/Kconfig* $n $(cat $Z/subsys/settings/Kconfig* | grep -c "CONFIG.*$n\|config $n")"
done
echo "settings_save_one declared: $(grep -c settings_save_one $Z/include/zephyr/settings/settings.h)"
echo "settings_load_subtree declared: $(grep -c settings_load_subtree $Z/include/zephyr/settings/settings.h)"
echo "nrf54l dts files naming storage_partition: $(grep -l storage_partition $Z/../nrf/dts/vendor/nordic/*54l* $Z/dts/arm/nordic/*54l* 2>&1 | wc -l)"
echo "files under the board folders of the nRF54L series that name SETTINGS_ZMS (list):"
grep -rl SETTINGS_ZMS $Z/boards/nordic/ 2>&1 | head -20
echo "files under the same folders that name SETTINGS_NVS (count): $(grep -rl SETTINGS_NVS $Z/boards/nordic/ 2>&1 | wc -l)"
echo "ZMS Kconfig depends-on text mentions RRAM (count): $(grep -c -i rram $Z/subsys/settings/Kconfig.zms $Z/subsys/fs/zms/Kconfig 2>&1 | tr '\n' ' ')"
echo "== K11 handler and retained memory"
echo "fatal.h names k_sys_fatal_error_handler: $(grep -c k_sys_fatal_error_handler $Z/include/zephyr/fatal.h)"
echo "kernel/fatal.c defines it weak (count of lines with both words): $(grep -c 'weak.*k_sys_fatal_error_handler\|k_sys_fatal_error_handler.*weak' $Z/kernel/fatal.c)"
echo "ztest source files defining it (count): $(grep -l 'k_sys_fatal_error_handler' $Z/subsys/testsuite/ztest/src/* 2>&1 | wc -l)"
echo "retained_mem bindings:"; ls $Z/dts/bindings/retained_mem/ 2>&1
echo "retained_mem_zephyr_ram driver present: $(ls $Z/drivers/retained_mem/retained_mem_zephyr_ram.c 2>&1 | wc -l)"
echo "retained_mem API header names retained_mem_read/write/clear: $(grep -c 'retained_mem_read\|retained_mem_write\|retained_mem_clear' $Z/include/zephyr/drivers/retained_mem.h)"
echo "== names the real file (rsy_hw_real.c) uses (counts of lines naming each; 0 = absent)"
for n in settings_load_subtree_direct settings_name_steq settings_save_one; do echo "settings.h $n $(grep -c $n $Z/include/zephyr/settings/settings.h)"; done
for n in flash_area_open flash_area_erase flash_area_write flash_area_read flash_area_close FIXED_PARTITION_EXISTS; do echo "flash_map.h/devicetree $n $(cat $Z/include/zephyr/storage/flash_map.h $Z/include/zephyr/devicetree/fixed-partitions.h | grep -c $n)"; done
for n in wdt_install_timeout wdt_setup wdt_feed WDT_FLAG_RESET_SOC WDT_OPT_PAUSE_HALTED_BY_DBG; do echo "watchdog.h $n $(grep -c $n $Z/include/zephyr/drivers/watchdog.h)"; done
for n in retained_mem_read retained_mem_write retained_mem_clear; do echo "retained_mem.h $n $(grep -c $n $Z/include/zephyr/drivers/retained_mem.h)"; done
echo "arm exception frame field names (count of lines naming each): pc $(grep -c 'pc;' $Z/include/zephyr/arch/arm/exception.h) lr $(grep -c 'lr;' $Z/include/zephyr/arch/arm/exception.h) xpsr $(grep -c 'xpsr' $Z/include/zephyr/arch/arm/exception.h) basic $(grep -c 'basic' $Z/include/zephyr/arch/arm/exception.h)"
echo "K10 more: files under the NCS folders naming SETTINGS_ZMS (count): $(grep -rl SETTINGS_ZMS /ws/nrf/samples /ws/nrf/boards /ws/nrf/applications 2>>/ws/out/u7-kfacts-stderr.txt | wc -l)"
echo "K10 more: nrf54l SoC and board files naming ZMS (count): $(grep -rl ZMS $Z/soc/nordic/nrf54l $Z/boards/nordic 2>>/ws/out/u7-kfacts-stderr.txt | wc -l)"
