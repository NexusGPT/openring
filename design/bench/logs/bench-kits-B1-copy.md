# Bench kits for the AI ring recorder

Listings as shown on 2026-11-10. Tags: [F] read on the maker's or seller's own page; [S] search-result text only, page not opened.
URL check: a HEAD request with curl on 2026-11-10 (log `url_check.log` in the evidence folder) returned 403, 404 or 500 for several pages that WebFetch read the same day. A page is marked [F] only when WebFetch returned its text; a page WebFetch refused is marked not read.
Evidence (saved quotes and the saved schematic text) is in `<scratch>/bench-evidence/`.

## 1. Main chip (nRF54LM20A): development kit, debugger, current measurement

**Kit: nRF54LM20 DK, maker Nordic Semiconductor**

- Order code: `NRF54LM20-DK` (Digi-Key part 1490-NRF54LM20-DK-ND) [F]. Nordic's DK page prints no order code [F, Nordic page `https://www.nordicsemi.com/Products/Development-hardware/nRF54LM20-DK`].
- SoC on the kit as sold: nRF54LM20B. Nordic's page says "Development kit featuring the nRF54LM20B wireless SoC" [F]. The Digi-Key description reads "NRF54LM20B WIRELESS SOC DEV KIT" [F]. The Digi-Key page also says the kit is for "the nRF54LM20A and nRF54LM20B" [F].
- Schematic of DK revision 0.5.4 (dated 23.01.2026) names the chip `nRF54LM20-PAAA-BE0` [F, saved schematic `dk_schematic_all.txt` lines 216, 268 "PRELIMINARY!"].
- Nordic compatibility matrix, per search text only: DK v0.3.4 and v0.5.4 used the nRF54LM20A; v0.7.0 onward uses the nRF54LM20B [S, `https://docs.nordicsemi.com/r/bundle/comp_matrix_nrf54lm20a/page/comp/nrf54lm20a/nrf54lm20a_ic_revision_overview.html`, not opened].
- **Gap for the ring:** the ring uses the nRF54LM20A in package CAAA (architecture.md section 2). No kit sold today is confirmed to carry the A die. Whether a v0.5.4 or v0.3.4 board can still be bought is not found.
- Pins brought out: GPIO headers P1, P2, P3, P4, P5 and P17; each has a power header P6, P7, P8, P9, P10, P18 giving 5.0 V from the power chip, 4 pins [F, Nordic `connector_if` page, quoted]. Pin-by-pin map: not read (the Nordic page's pin tables are port-to-function lists, not pin numbers [F]). Also P13 (2x5, 1.27 mm, debug out, trace) and P12 (2x10, 1.27 mm) [F, schematic lines 5162, 5206]. Nordic page: "Two UART interfaces through virtual serial ports" [F].
- On-board debugger: SEGGER J-Link OB [F, Nordic page].
- USB: two USB-C 2.0 connectors, one "nRF USB Connector" (lines 5005, 5068) and one "Debugger USB Connector" (lines 5090, 5133) [F, saved schematic].
- Supply and logic: VDD:nRF = VDD:IO = 1.8 to 3.6 V, set by the on-board power chip nPM1300 (schematic line 3897) [F]. 5 V from USB [F, schematic line 2773 "DK requires power from USB connector"].
- Current measurement: yes. Nordic's set-up page: "Remove the jumper from the P14 header" and "replace the measurement devices on P14 with the jumper" [F, Nordic `set_up_dk.html`, quoted lines 49 and 51]. Schematic block "Current Measurement" holds P14 (1x3, line 3739-3740) and JP1 "Shunt 2.54mm" (lines 3748-3749) [F]; JP1's exact role is not read.
- Power Profiler Kit II: supported on all Nordic DKs [F, PPK2 page, below].
- Caveat [S]: a DevZone user reading 89 µA on an nRF54LM20A DK in series at the VDD nRF header, against a 4 µA datasheet figure; no confirmed answer found (`https://devzone.nordicsemi.com/f/nordic-q-a/126766/nrf54lm20a-dk-sleep-current-much-higher-than-datasheet-measuring-89-a-vs-4-a`).
- Price: **US$45.00 per unit** (box, quantity 1), Digi-Key US, In-Stock 321, Manufacturer Standard Lead Time 19 weeks, as shown 2026-11-10 [F] `https://www.digikey.com/en/products/detail/nordic-semiconductor-asa/NRF54LM20-DK/27685498`.
- Other sellers [S, search text, not opened]: Futureelectronics about $44.48, 9 in stock; element14 Singapore S$58.97 (ex tax); Digi-Key Taiwan NT$1,365.00 with zero stock. Mouser: no listing for this kit found.

**Power Profiler Kit II, order code `nRF-PPK2`, maker Nordic Semiconductor**

- Order code `nRF-PPK2` [F, `https://www.nordicsemi.com/startppk2`: "Ordering code: nRF-PPK2"].
- Range: 200 nA to 1 A [F, same page]. "Support for all Nordic DKs, in addition to custom HW" [F, same page].
- Price: **US$107.30 per unit**, Digi-Key US part 1490-NRF-PPK2-ND, In-Stock 1,608, lead time 16 weeks, as shown 2026-11-10 [F] `https://www.digikey.com/en/products/detail/nordic-semiconductor-asa/NRF-PPK2/13557476`.
- Other [S]: Nordic launch price $89 (CNX Software, 2020); Jameco $150.95, undated; Digi-Key Australia AUD 140.69 ex GST, undated snippet.

**Not found / not read**
- Mouser listing for the nRF54LM20 DK: not found in the search results.
- User guide v0.3.4 (the A-era guide): the Mouser PDF link returned "Access to this page has been denied" (HTML, not a PDF). It is saved as `design/datasheets/bench_nrf54lm20-dk-hw-ug-v0.3.4.pdf` and is not a readable PDF; not read. I did not work around the block.
- DK pin-by-pin header map for the A die: not read.

## 2. Power chip (nPM1300): evaluation kit

**Kit: nPM1300-EK ("nPM1300 EK Evaluation Kit"), maker Nordic Semiconductor**

- Order code: `NPM1300-EK` (Digi-Key part 1490-NPM1300-EK-ND) [F, Digi-Key page]. Nordic's product page prints no order code [F, `https://www.nordicsemi.com/Products/Development-hardware/npm1300-ek`].
- Price: **US$64.35 per unit** (box, quantity 1); US$64.15 at 20, US$64.11 at 40, US$64.05 at 100. Digi-Key US, In-Stock 158, Manufacturer Standard Lead Time 16 weeks, as shown 2026-11-10 [F] `https://www.digikey.com/en/products/detail/nordic-semiconductor-asa/NPM1300-EK/19722486`.
- Other sellers [S, search text only, not opened]: Digi-Key UK £47.66 ex VAT, 74 in stock; Digi-Key Canada CAD 95.14; Digi-Key Singapore about $87.40 ex VAT (currency not stated in snippet).
- Battery connectors: "JST battery connectors support batteries with or without an internal NTC"; 2- and 3-terminal batteries [F, Nordic product page]. Connector pinout not read: the EK user guide PDF (`https://infocenter.nordicsemi.com/pdf/nPM1300_EK_User_Guide_v1.1.0.pdf`) returned a Cloudflare "Just a moment..." challenge, saved as `design/datasheets/bench_npm1300-ek-ug-v1.1.0.pdf` (HTML, not a PDF, not read). I did not work around it.
- Outputs: "Easy access to PMIC voltage outputs through male pin headers and probe loops" [F, `https://docs.nordicsemi.com/r/bundle/ug_npm1300_ek/page/ug/npm1300_ek/intro.html`]. Header designators for VOUT1 and VOUT2: not read. Nordic's measurement page, search text only, names P4 and P5 for VOUT1 and VOUT2 and P1 for VBAT [S].
- Load switches and LDOs: "Two 100 mA load switches / 50 mA LDOs" [F, same page]. Whether the EK wires both to pins: not read.
- Control: "Controlled using Inter-integrated Circuit (I2C) compatible TWI" [F, same page]. TWI header pins: not read. Logic level set by VDDIO on the PMIC [S, DevZone search text only]; the EK's VDDIO value not read.
- USB: "Dedicated Universal Serial Bus (USB) Type-C connection to power the nPM1300 PMIC" [F, `https://nrfconnectdocs.nordicsemi.com/ncs/latest/zephyr/boards/shields/npm1300_ek/doc/index.html`]. Input voltage: not read.
- Other [F, Nordic product page]: three LEDs and four pushbuttons; male pin headers for all PMIC pins and the battery connectors, for connecting to Nordic DKs and test equipment; configured through the nPM PowerUP app.
- PMIC buck output range, from the DK schematic's nPM1300 settings (not the EK): "VOUT1: 1.8V - 3.3V, max 200mA" and "VOUT2: 1.8V - 3.3V, max 200mA" [F, `dk_schematic_all.txt`, line 3890].

**Not found / not read:** EK pin table, JST pinout, VDDIO on the EK, the EK's header designators for the buck outputs, the TWI header and the battery connector. These are in the user guide, which was blocked.


## 3. Microphones (PDM): Infineon evaluation kits and breakouts

**Kit for IM68D128BV01 (the ring's IM68D128B part): `KITIM68D128BV01FLEXTOBO1`, maker Infineon**

- Name check: Digi-Key lists "EVAL BOARD FOR IM68D128BV01", Digi-Key part 448-KITIM68D128BV01FLEXTOBO1-ND, manufacturer part number KITIM68D128BV01FLEXTOBO1 [F, `https://www.digikey.com/en/products/detail/infineon-technologies/KITIM68D128BV01FLEXTOBO1/26668383`]. The name `KIT_IM68D128BV01_FLEX` is an alias only in a Mouser India search snippet [S, `https://www.mouser.in/c/?marcom=137411652`].
- Price: **US$75.19 per unit** (box, quantity 1); US$75.02 at 10, US$74.95 at 25, US$74.84 at 100. In-Stock 9; Manufacturer Standard Lead Time 97 weeks; part status Active. As shown 2026-11-10 [F, Digi-Key US page above].
- Other sellers [S, search text only]: Element14 Australia order code 4707491, about US$108.57 each before GST (`https://au.element14.com/infineon/kitim68d128bv01flextobo1/flex-evaluation-kit-mems-microphone/dp/4707491`); Mouser SKU 726-KITIM68D128BV01F, "In Stock: 27" at the time of the snapshot (`https://www.mouser.in/c/?marcom=137411652`).
- Contents: five flex boards, each with one microphone, and one adapter board [S, Mouser India and Element14 AU search text, not opened]. The Infineon page for the kit (`https://www.infineon.com/evaluation-board/KITIM68D128BV01FLEXTOBO1`) returned HTTP 404 to WebFetch; a later curl HEAD returned 200, but the page was not read. The count is not confirmed on the maker's page.
- Connector: flex boards to the adapter by a 6-position ZIF connector [S, Mouser India search text]. Not read on the maker's page.
- Supply and logic: IM68D128BV01 supply 1.6 to 3.465 V [S, Digi-Key bare-part search text, `https://www.digikey.at/en/products/detail/infineon-technologies/IM68D128BV01XTMA1/26668380`, not opened]; the kit's own voltage not read.

**Kit for IM73D122V01 (the architecture's microphone): `KITIM73D122V01FLEXTOBO1`, maker Infineon**

- Name check: Digi-Key lists "EVAL BOARD FOR IM73D122V01", Digi-Key part 448-KITIM73D122V01FLEXTOBO1-ND, manufacturer part number KITIM73D122V01FLEXTOBO1 [F, `https://www.digikey.com/en/products/detail/infineon-technologies/KITIM73D122V01FLEXTOBO1/16999573`]. `KIT_IM73D122V01_FLEX` is the name RS Components uses [S, `https://my.rs-online.com/web/p/analogue-development-tools/2601014`; curl HEAD returned 404 on 2026-11-10, search text only]. `EVAL_IM73D122V01_FLEX` is not found in any result.
- Price: **US$75.19 per unit** (bulk table as shown: US$75.02 at 10, US$74.95 at 25, US$74.84 at 100). In-Stock 0; Manufacturer Standard Lead Time 97 weeks; part status Active. As shown 2026-11-10 [F, Digi-Key US page]. The two Digi-Key kit pages show the same price table; confirm on the live page before use.
- Other [S]: RS stock 260-1014, "Currently unavailable"; Element14 Singapore order page (`https://sg.element14.com/infineon/kitim73d122v01flextobo1/dev-kit-mems-microphone/dp/4125803`) with 32-week lead time; element14 New Zealand about NZ$170.08 incl. GST.
- Contents: five flex boards and one adapter board [S, search text of RS and Element14 pages].
- Supply: IM73D122V01 1.62 to 3.6 V [S, Digi-Key bare-part search text, `https://www.digikey.fi/en/products/detail/infineon-technologies/IM73D122V01XTMA1/16999563`].

**Third-party PDM breakout carrying either part**

- Not found. The search `PDM microphone breakout board Infineon IM73D122 OR IM68D128B breakout module` returned only bare-part listings and one OSH Park board for a different microphone (INMP621, `https://oshpark.com/shared_projects/fVL5GGKG`), which is a community design with no guarantee of function [S].

**Caveat**
- A Digi-Key page for the IM73D122 kit shows part status Active with 0 in stock, while a Digi-Key Canada page shows the same kit as Discontinued [S]. Check with the seller.
- The Digi-Key kit price is identical across the two kits, which may be a page-read artefact. Not confirmed.

## 4. Screen: 0.95 inch 120 x 240 AMOLED with adapter and example code

**Result: no seller found that sells a 0.95 inch 120 x 240 AMOLED panel bundled with a breakout or adapter board and example code. Partial matches below.**

- **BuyDisplay (ER-OLED0.95-4C family, SH8501 driver):** the listing `https://www.buydisplay.com/0-95-inch-micro-full-color-amoled-display-panel-rgb-120x240-sh8501-spi` returned HTTP 403 to WebFetch: **not read**. Search text only [S]: a bare panel, ¥25.43 per unit, volume ¥22.71 at 100. The "ER-OLEDM0.95" name was not found; the search returned ER-OLED0.95-4C. Its 8051 development board `https://www.buydisplay.com/8051-microcontroller-development-board-for-tft-display-er-oled0-95-4c` also returned HTTP 403: **not read**. Search text [S]: an STC12LE5A60S2 8051 board, with demo code "download" for the 4C series.
- **Gesight (TR095A120SPC, LTPS AMOLED 120 x 240 SPI):** `https://gesight.com/product/0-95-inch-ltps-amoled-display-120x240-spi` returned HTTP 500: **not read**. Search text [S]: US$22.48 per piece; "demo kit setup", "a free convertor board" and connectors; whether example code is included is not stated in the snippet.
- **Waveshare:** no 120 x 240 AMOLED with RM69310 or SH8501 found. Its 0.95 inch RGB OLED products are 96 x 64 SSD1331 modules [S, `https://www.waveshare.com/product/displays/oled/0.95inch-rgb-oled-a.htm`].
- **Panox (BO095F120S, RM69310, 4-SPI), maker datasheet:** saved as `design/datasheets/bench_panox-bo095f120s.pdf` (19 pages), read from its saved text [F]:
  - Driver IC RM69310, interface 4-SPI, 120 x 240, 16.7 M colours, active area 10.8 (H) x 21.6 (V) mm (`panox_bo095f120s.txt` lines 122, 123, 156).
  - 20 pins, numbered 1 to 20 (line 245 onward). Pin names include ELVDD, ELVEE, VCI, VDDIO, SWIRE, NC, LCD_CS (lines 254 to 258).
  - Voltages: ELVDD +4.6 V (lines 383, 393, 455); ELVEE / ELVSS -2.4 V (line 459; ELVEE pin label at line 311); VCI 2.4 to 3.3 V (rating table, line 442); IOVDD 1.65 to 3.3 V [F, lines 379 to 459].
  - SWIRE: "Setting DC/DC Power IC output voltage" [F, `panox_bo095f120s.txt` pin table, line ~ 314]. The panel needs the DC/DC IC output set by this pin. Whether that IC sits on the module or the adapter is not stated.
  - Connector: drawing label "连接器0.51mm" (connector 0.51 mm) and "FPC 0.13mm" (line 228). Pitch is not stated.
  - Example code: "Recommended Setting and Initialization Flow for Reference ... Please refer to attached file" (page 9, line 520). The attached file is not in the PDF. Panox's own note on a config.txt is for its HDMI controller board [S, search text].
- **Tailor Pixels TOH095XVT-01 (the ring's panel):** datasheet saved locally as `design/datasheets/display_TOH095XVT-01.pdf`; not re-read for this section. The Tailor Pixels page is the maker's source for the start-up code (architecture.md action 12.1).

**Not found / not read**
- Adapter or breakout with example code for SH8501 or RM69310 panels from DWO, Panox or Waveshare: searched "0.95 inch 120x240 AMOLED ... breakout adapter ... example code" and "... Panox DWO" (WebSearch, standard); no such listing in the results.
- Order code and price for a bundle: not read (both seller pages refused or failed).
- Whether +4.6 V and -2.2 V (ring's SGM38046 values) are made on the adapter: not found. The Panox datasheet gives ELVEE -2.4 V, not -2.2 V.

## 5. Storage: SD NAND or microSD breakout

- **Adafruit SPI Flash SD Card, XTSD 4 GB, product ID 6039** (maker Adafruit; the chip is an XTX XTSD part, not the ring's CS part). Capacity 4 GByte; SPI mode with a level shifter; 3.3 V regulator; "3V or 5V logic"; CS pull-up [F, `https://adafruit.com/product/6039`]. Pins named in the caption: MISO, SCK, MOSI, VIN, GND [F, same page]. Price **US$12.50** (1 to 9), US$11.25 (10 to 99), US$10.00 (100+), as shown 2026-11-10 [F]. Stock: **Out of stock** [F].
- **Adafruit microSD card breakout board+, product ID 254** (a stand-in, microSD card not included; capacity set by the card): price **$7.50** (currency sign only on the page; Adafruit's US prices are USD) [F, `https://www.adafruit.com/product/254`]. Stock: "In stock" [F]. 3 V level shifting; onboard 5 V to 3 V regulator, 150 mA [F]. Header: 0.1 inch header supplied unattached [F]. Arduino wiring given: GND, 5V, CLK to pin 13, DO to pin 12, DI to pin 11, CS to pin 10 [F].
- **CS Semiconductor CSNP32GCR01-BOW (the ring's SD NAND, 4 GB, LGA-8, 8.0 x 6.2 mm)**: part listed at LCSC (`https://lcsc.com/product-detail/NAND-FLASH_CS-Semiconductor-CSNP32GCR01-BOW_C5440134.html`) with 2.7 to 3.6 V and an SD interface [S, search text]. SPI-mode pin table not read. Price not read.
- **Breakout for the CSNP32GCR01**: not found. Search `CSNP32GCR01-BOW 4GB SD NAND breakout board SPI 3.3V` returned the chip listing and the Adafruit XTSD boards only [S].
- **MK-Founder evaluation board**: not found. Search `MK-Founder SD NAND evaluation board SPI breakout CSNP32GCR01 Adafruit or sparkfun` returned no MK-Founder board and no SparkFun board [S].

## 6. Vibration: Vybronics motors and MOSFET stand-in

- **VC0625B001L, Vybronics, Digi-Key part 1670-VC0625B001L-ND** [F, `https://www.digikey.com/en/products/detail/vybronics-inc/VC0625B001L/12323586`]: "VIBRATION ERM MOTOR 10K RPM 0.2G"; rated **3VDC**; 6.00 mm diameter; wire leads; Active. Price **US$3.17** (1), US$2.91 (5), US$2.81 (10), US$2.49 (100), tray, as shown 2026-11-10 [F]. Stock: In-Stock 8,079; lead time 9 weeks [F]. Start voltage and current: not listed on the page [F].
  - Discrepancy: architecture.md section 16.4 gives "rated 2.5 V, 100 mA maximum, starts at 2.0 V" from a maker spec (`design/parts/slim-2.md`, not opened by me). The Digi-Key page says 3VDC. Open item (questions_for_owner).
- **VC0720B088L, Vybronics, Digi-Key part 1670-VC0720B088L-ND** [F, `https://www.digikey.com/en/products/detail/vybronics-inc/VC0720B088L/15220802`]: "VIBRATION ERM MOTOR FPC 3V 0.3G"; rated 3VDC; 7.00 mm diameter; FPC style (not wire leads). Price **US$3.23** (1), US$2.97 (5), US$2.86 (10), US$2.53 (100), as shown 2026-11-10 [F]. In-Stock 714; lead 9 weeks [F]. Start voltage and current not listed [F].
- **Stand-in MOSFET driver: Adafruit MOSFET Driver, STEMMA JST PH 2 mm, product ID 5648** [F, `https://www.adafruit.com/product/5648`]. Price **$3.95** (1 to 9 tier; currency sign only). In stock [F]. MOSFET AO3406, N-channel, 30 V, 3.6 A peak, 70 mΩ [F]. Signal input 3 V to 20 V logic; power input 3 V to 30 V [F]. Three-pin connector with terminal blocks [F, caption]. Low side only, so it switches the motor's negative side.

## 7. Switches and battery

- **Alps SKTAAAE010, single unit**: no seller page was read. A Digi-Key US page was not found in search. Search-text figures only [S]: aggregator Zenode quotes Digi-Key cut tape at about $0.71 for one unit (not read on Digi-Key); Ciiva shows a Digi-Key Germany stock of 48,817 with no date; an Avnet listing shows 0 in stock, 140 weeks factory lead time and a 20,000-piece minimum at about $0.13. Spec from LCSC/aggregator text: SPST-NO top-actuated SMD tactile switch, 50 mA, 12 V [S]. Conflicting stock figures: unverified.
- **Battery: SparkFun Polymer Lithium Ion Battery 40 mAh (JST-PH), SKU PRT-13852** [F, `https://www.sparkfun.com/products/13852`]. Price **$7.14** (currency sign only) [F]. Stock: "In stock" [F]. Capacity 40 mAh rated [F]. Nominal voltage 3.70 V [F]. Connector: "standard 2-pin JST-PH connector - 2mm spacing between pins" [F]. Protection: "built-in protection against over voltage, over current, and minimum voltage" [F]; the page does not use the term PCM.
  - **Not verified:** that the nPM1300 EK accepts this cell. The EK's JST pinout and the charge setting were not read (section 2). The architecture asks for a 4.35 V or 4.4 V cell (section 16.4); this cell is 3.70 V nominal. Its maximum charge voltage is not read on the page.
- Other [S]: Thingbits (India) 40 mAh cell with a built-in protection module, INR 109.00 (`https://thingbits.in/products/lithium-ion-polymer-battery-3-7v-40mah`).

## 8. Reference device: Plaud recorders

Prices and specs from `https://www.plaud.ai/pages/compare-plaud-devices` [F] (USD; wording "during pre-order" and "upon official release"):

| Model | Price (USD) | Microphones | Continuous recording | Battery | Storage | Status on page |
|---|---|---|---|---|---|---|
| Plaud Note Pro | $189.00 | 4 MEMS, 1 VPU | up to 30 h (Enhance mode) | 500 mAh | 64 GB | pre-order now, release later at same price |
| Plaud Note | $159.00 | 2 MEMS, 1 VPU | up to 30 h | 400 mAh | 64 GB | pre-order now |
| Plaud NotePin S | $179.00 | 2 MEMS | up to 20 h | 320 mAh | 64 GB | pre-order now |
| Plaud NotePin | $159.00 | 2 MEMS | up to 20 h | 270 mAh | 64 GB | pre-order now |
| Plaud One | $249.99 | 3 MEMS + 1 VPU in earbuds; 4 MEMS in case per third-party [S] | up to 6 h earbuds, 25 h case | not read | not read | "New arrival"; Explorer Edition pre-order [F, `https://www.plaud.ai/pages/ai-recording-devices`] |

- Standby: 60 days (Note Pro, Note), 40 days (NotePin S, NotePin) [F, compare page].
- The `ai-recording-devices` page shows Note Pro $189.00 and NotePin S $179.00, and shows no price for Note and NotePin [F]. The compare page is the source for the $159.00 price of both. Conflicting on the same site; not resolved.
- "On sale today": every model except Plaud One is shown as pre-order on the compare page [F]. No retail "buy now" price was found.
- Export of raw audio: Plaud help centre "Export files" article `https://support.plaud.ai/hc/en-us/articles/50835453223705-Export-files` returned HTTP 403: **not read**. Search text only [S]: original audio exported as MP3 or WAV; WAV on Plaud App; Plaud Web MP3 only. No source found gives the sample rate, bit depth or MP3 bitrate.

## 9. Measurement method sources

- **LibriSpeech (test-clean)**, `https://www.openslr.org/12` [F]: "License: CC BY 4.0"; the corpus is "16kHz read English speech"; test-clean is `test-clean.tar.gz [346M]`.
- **ITU-T P.501 (04/2025), Test signals for use in telephony and other speech-based applications**, `https://www.itu.int/dms_pubrec/itu-t/rec/p/T-REC-P.501-202504-I!!SUM-HTM-E.htm` [F]: "Annex B provides speech files and noise sequences to be used in combination with objective speech quality evaluation methods." The licence text for the files was not found on this page; the ITU-T test signal database is the download source [S].
- **ITU-T P.50, artificial voice**, `https://itu.int/ITU-T/P.50` [S, search text, not opened]: defines an artificial voice that reproduces human speech characteristics, in female and male forms. The 60 dB SPL at 1 m level was not found in P.50 search text: not found.
- **jiwer (word error rate)**, `https://github.com/jitsi/jiwer` [F]: "Evaluate your speech-to-text system with similarity measures such as word error rate (WER)"; Apache-2.0 licence; function `wer(reference, hypothesis)`.
- **Whisper (open speech-to-text model)**, `https://github.com/openai/whisper` [F]: code and weights under the MIT License; install `pip install -U openai-whisper`; model names tiny to turbo.
- **How a vendor measured meeting recorders (WER at distance)**: `https://www.plaud.ai/blogs/news/inside-plaud-s-anechoic-chamber` [F]: two distances (1 m and 3 m); transcripts scored against a reference text by WER; three noise levels "quiet (~35 dB), moderate (~55 dB), and loud (~70 dB)"; speaker count, speech level and sample count not stated. Vendor's own test, not neutral.
- **Third-party method**: UMEVO guide `https://www.umevo.ai/blogs/ume-all-posts/best-ai-voice-recorder-2025-complete-guide-for-students-journalists-professionals` [S, search text]: three reviewers transcribed 10-minute samples; WER = (substitutions + deletions + insertions) / words. UMEVO sells competing hardware.
- **Not found**: a neutral, documented head-to-head WER table at distance for these recorders. Search `AI meeting recorder hardware test word error rate measured at distance ... Plaud NotePin review method` returned vendor pages only.

## questions_for_owner

1. The nRF54LM20 DK sold today (Digi-Key NRF54LM20-DK, Nordic page) is described as carrying the nRF54LM20B. The ring uses the nRF54LM20A (CAAA). Decide whether a B-based bench is acceptable, or whether an A-based board (DK v0.5.4 or earlier, not found for sale) is needed.
2. Vybronics VC0625B001L: architecture.md section 16.4 says rated 2.5 V, 100 mA, starts at 2.0 V. Digi-Key says 3VDC rated, with no start voltage or current listed. Which figure is the design input?
3. Battery: the cell found (SparkFun PRT-13852) is 3.70 V nominal. The architecture asks for a 4.35 V or 4.4 V cell at 40 mAh. The nPM1300 EK's JST pinout was not read (user guide blocked). Confirm the EK connector before buying a cell.
4. Two blocked downloads are saved in `datasheets/` as `bench_nrf54lm20-dk-hw-ug-v0.3.4.pdf` and `bench_npm1300-ek-ug-v1.1.0.pdf`. Each is an HTML block page, not a PDF. I left them in place (not deleted by me). Remove them, or ask me to retry them later.
5. Infineon kit: the five-microphone count and the 6-position ZIF connector come from search text only; the Infineon kit page returned 404. Confirm with the seller before ordering.
RESULT: done, 9 sections written; section 1 found the sold DK carries the nRF54LM20B, not the A die; sections 4, 5 and 7 have gaps (no screen bundle, no SD NAND breakout, Alps and battery pinout unverified), and the nPM1300 EK pinout and Plaud export specs are not read.
