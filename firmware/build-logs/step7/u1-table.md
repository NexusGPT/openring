| U1 net | ball | chip pin | devicetree node or property | used by which driver file | status |
|---|---|---|---|---|---|
| ANT1_NODE | C1 | ANT | `radio` (fixed function of the chip) | kit Bluetooth controller (radio) | builds only |
| BTN_REC | H2 | P0.04 | `ring_btn_rec` property `gpios` | none: no joystick driver exists (app/src/main.c l.13-14: "the driver calls rglue_input()", not written); kit gpio-keys driver not enabled (CONFIG_INPUT off) | not used yet |
| DBG_TX | B4 | P1.15 | `uart20` pin control, function `UART_TX` (default and sleep) | kit uart_nrfx_uarte.c (the console) | builds only |
| DCC | A5 | DCC | none (the DC/DC converter's inductor L1 (vregmain's mode is set in the devicetree, no pin)) | none | no node by nature |
| DECA | A8 | DECA | none (decoupling) | none | no node by nature |
| DECA | B2 | DECRF | none (decoupling) | none | no node by nature |
| DECD | A6 | DECD | none (decoupling) | none | no node by nature |
| GND | A7 | VSS | none (ground) | none | no node by nature |
| GND | D3 | VSS | none (ground) | none | no node by nature |
| GND | E1 | VSS | none (ground) | none | no node by nature |
| GND | F10 | VSS | none (ground) | none | no node by nature |
| JOY_DOWN | G2 | P0.07 | `ring_joy_down` property `gpios` | none: no joystick driver exists (app/src/main.c l.13-14: "the driver calls rglue_input()", not written); kit gpio-keys driver not enabled (CONFIG_INPUT off) | not used yet |
| JOY_LEFT | G1 | P0.08 | `ring_joy_left` property `gpios` | none: no joystick driver exists (app/src/main.c l.13-14: "the driver calls rglue_input()", not written); kit gpio-keys driver not enabled (CONFIG_INPUT off) | not used yet |
| JOY_RIGHT | G10 | P1.31 | `ring_joy_right` property `gpios` | none: no joystick driver exists (app/src/main.c l.13-14: "the driver calls rglue_input()", not written); kit gpio-keys driver not enabled (CONFIG_INPUT off) | not used yet |
| JOY_UP | H1 | P0.06 | `ring_joy_up` property `gpios` | none: no joystick driver exists (app/src/main.c l.13-14: "the driver calls rglue_input()", not written); kit gpio-keys driver not enabled (CONFIG_INPUT off) | not used yet |
| LCD_CS | F7 | P1.05 | `spi21` property `cs-gpios` | none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); the MIPI DBI node has no driver (CONFIG_MIPI_DBI off) | not used yet |
| LCD_DCX | G7 | P1.06 | `ring_lcd_dbi` property `dc-gpios` | none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); the MIPI DBI node has no driver (CONFIG_MIPI_DBI off) | not used yet |
| LCD_MOSI | G8 | P1.04 | `spi21` pin control, function `SPIM_MOSI` (default and sleep) | none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); the MIPI DBI node has no driver (CONFIG_MIPI_DBI off) | not used yet |
| LCD_RST | H5 | P1.07 | `ring_lcd_dbi` property `reset-gpios` | none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); the MIPI DBI node has no driver (CONFIG_MIPI_DBI off) | not used yet |
| LCD_SCK | G9 | P1.03 | `spi21` pin control, function `SPIM_SCK` (default and sleep) | none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); the MIPI DBI node has no driver (CONFIG_MIPI_DBI off) | not used yet |
| LCD_TE | F4 | P1.14 | `ring_lcd_dbi` property `te-gpios` | none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); the MIPI DBI node has no driver (CONFIG_MIPI_DBI off) | not used yet |
| MIC_A_CLK | F1 | P1.13 | `pdm20` pin control, function `PDM_CLK` (default and sleep) | modules/ring_audio/src/rau_hw_real.c through kit dmic_nrfx_pdm.c | builds only |
| MIC_A_DATA | F2 | P1.11 | `pdm20` pin control, function `PDM_DIN` (default and sleep) | modules/ring_audio/src/rau_hw_real.c through kit dmic_nrfx_pdm.c | builds only |
| MIC_B_DATA | D7 | P1.25 | `/zephyr,user` property `mic-b-data-gpios` | none, by design: a test pad the firmware never configures (design/firmware.md l.77) | not used yet |
| MOTOR | F6 | P3.01 | `ring_motor` property `gpios` | modules/ring_motor/src/rmo_hw_real.c (alias ring-motor) | builds only |
| NRESET | E2 | nRESET | none (reset, test pad TP5) | none | no node by nature |
| OLED_PWR_EN | F9 | P1.30 | `/zephyr,user` property `oled-pwr-en-gpios` | none: no screen supply code (zephyr,user property only) | not used yet |
| PMIC_INT | D8 | P1.28 | `ring_pmic` property `host-int-gpios` | kit mfd_npm13xx.c, i2c_nrfx_twim.c (rpw_hw_real.c would use it: not compiled, CONFIG_RING_POWER_REAL=n) | builds only |
| PMIC_SCL | E7 | P1.27 | `i2c22` pin control, function `TWIM_SCL` (default and sleep) | kit mfd_npm13xx.c, i2c_nrfx_twim.c (rpw_hw_real.c would use it: not compiled, CONFIG_RING_POWER_REAL=n) | builds only |
| PMIC_SDA | B8 | P1.26 | `i2c22` pin control, function `TWIM_SDA` (default and sleep) | kit mfd_npm13xx.c, i2c_nrfx_twim.c (rpw_hw_real.c would use it: not compiled, CONFIG_RING_POWER_REAL=n) | builds only |
| SD_CS | D9 | P2.05 | `spi00` property `cs-gpios` | modules/ring_store/src/rst_hw_real.c through kit sdhc_spi.c, spi_nrfx_spim.c | builds only |
| SD_MISO | D10 | P2.04 | `spi00` pin control, function `SPIM_MISO` (default and sleep) | modules/ring_store/src/rst_hw_real.c through kit sdhc_spi.c, spi_nrfx_spim.c | builds only |
| SD_MOSI | B10 | P2.02 | `spi00` pin control, function `SPIM_MOSI` (default and sleep) | modules/ring_store/src/rst_hw_real.c through kit sdhc_spi.c, spi_nrfx_spim.c | builds only |
| SD_SCK | A9 | P2.01 | `spi00` pin control, function `SPIM_SCK` (default and sleep) | modules/ring_store/src/rst_hw_real.c through kit sdhc_spi.c, spi_nrfx_spim.c | builds only |
| SPARE_P1_00 | H10 | P1.00 | `/zephyr,user` property `spare-p1-00-gpios` | none, by design: a test pad the firmware never configures (design/firmware.md l.77) | not used yet |
| SPARE_P2_00 | A10 | P2.00 | `/zephyr,user` property `spare-p2-00-gpios` | none, by design: a test pad the firmware never configures (design/firmware.md l.77) | not used yet |
| SPARE_P3_03 | F5 | P3.03 | `/zephyr,user` property `spare-p3-03-gpios` | none, by design: a test pad the firmware never configures (design/firmware.md l.77) | not used yet |
| SPARE_P3_04 | G5 | P3.04 | `/zephyr,user` property `spare-p3-04-gpios` | none, by design: a test pad the firmware never configures (design/firmware.md l.77) | not used yet |
| SWDCLK | D5 | SWDCLK | none (debug, test pad TP3) | none | no node by nature |
| SWDIO | E4 | SWDIO | none (debug, test pad TP4) | none | no node by nature |
| TXRTUNE | G6 | TXRTUNE | none (radio tuning resistor R2) | none | no node by nature |
| U1_VBUS | H9 | VBUS | `zephyr_udc0` (fixed function of the chip) | modules/ring_xfer/src/rxf_hw_real.c through kit udc_dwc2.c | builds only |
| USB_DN | H6 | D- | `zephyr_udc0` (fixed function of the chip) | modules/ring_xfer/src/rxf_hw_real.c through kit udc_dwc2.c | builds only |
| USB_DP | H7 | D+ | `zephyr_udc0` (fixed function of the chip) | modules/ring_xfer/src/rxf_hw_real.c through kit udc_dwc2.c | builds only |
| VDD_1V8 | A4 | VDD | none (supply) | none | no node by nature |
| VDD_1V8 | E10 | VDD | none (supply) | none | no node by nature |
| VDD_USB_3V3 | H8 | DECUSB | none (the chip's USB regulator output (DECUSB), a capacitor only) | none | no node by nature |
| XC1 | A2 | XC1 | `hfxo` (fixed function of the chip) | kit clock control (HFXO); rau_hw_real.c requests it | builds only |
| XC2 | A1 | XC2 | `hfxo` (fixed function of the chip) | kit clock control (HFXO); rau_hw_real.c requests it | builds only |
| XL1 | B6 | P1.20 | `lfxo` (fixed function of the chip) | kit clock control (LFXO, the GRTC's clock) | builds only |
| XL2 | B7 | P1.21 | `lfxo` (fixed function of the chip) | kit clock control (LFXO, the GRTC's clock) | builds only |
| (no net) | B5 | P1.16 | none | none | not connected on the ring board |
| (no net) | B9 | P2.03 | none | none | not connected on the ring board |
| (no net) | D6 | P1.22 | none | none | not connected on the ring board |
| (no net) | E5 | P1.19 | none | none | not connected on the ring board |
| (no net) | E6 | P1.24 | none | none | not connected on the ring board |
| (no net) | E8 | P1.01 | none | none | not connected on the ring board |
| (no net) | E9 | P1.29 | none | none | not connected on the ring board |
| (no net) | F8 | P1.02 | none | none | not connected on the ring board |
| (no net) | G4 | P3.05 | none | none | not connected on the ring board |
| (no net) | H4 | P0.03 | none | none | not connected on the ring board |

u1_table: 61 rows of U1
