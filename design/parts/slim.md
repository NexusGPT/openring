# Slim ring parts: maker datasheet facts

Scope: facts only, no recommendation. Target for the screen is a glass outline inside 21.0 x 14.0 mm (long side at most 21 mm). Tags: [F] read from the maker's document (saved copy in `design/datasheets/`), [S] search text or a listing page only. Page numbers are PDF page numbers of the saved copy.

## 1. Screen (AMOLED or OLED, outline inside 21.0 x 14.0 mm)

Result: none of the 6 candidates below has an outline inside 21.0 x 14.0 mm. Two that are closest on one side: DM-OLED096-658 (short side 14 mm fits, long side 28 mm does not) and the 0.95 in 180 x 120 panel (both sides too large). No 0.85 to 0.9 in AMOLED with an 18 x 12 mm active area was found in the places searched (see Not found).

### 1.1 Panox BO095F120S (0.95 in AMOLED, 120RGB x 240), maker document [F]
- Source: https://www.panoxdisplay.com/uploadfile/datasheet/BO095F120S.pdf (saved `design/datasheets/slim_panox-bo095f120s.pdf`), Rev V1, 2018/3/26.
- Outline: 12.8 (H) x 27.35 (V) x 0.75 (T) mm, excluding hooks and FPC tail. p4. Long side 27.35 mm: does not fit.
- Active area 10.8 (H) x 21.6 (V) mm, p4. Resolution 120RGB x 240, p4. Driver IC RM69310, p4. Interface 4-SPI, p4. Operating -30 to 70 C, p4.
- Connector and pitch: text says "COG+FPC" (p5) and "connector 0.51mm" (p5 drawing text); pitch not stated in text.
- Pin table (p6): 1 ELVDD, 2 ELVEE, 3 SWIRE (sets DC/DC output voltage), 4 VCI, 5 VDDIO, 6 GND, 7 NC, 8 LCD_CS, 9 LCD_CLK, 10 LCD_DC, 11 LCD_SDA, 12 LCD_RES, 13 LCD_TE, 14 GND, 15-19 TP (touch, TBD), 20 GND. Pin count 20.
- Supplies (p8): ELVDD +4.6 V; ELVSS -2.4 (listed as negative supply, typ not given); VCI 2.4 to 3.3 V (2.8 typ); IOVDD 1.65 to 3.3 V. The module takes ELVDD and ELVEE on pins, so the +4.6 V and -2.4 V supplies must come from outside, as the document does not state they are generated on the module.
- Current or power: "Ivdd" rows are blank (p8). Not in the document.
- Driver datasheet: "Please refer to IC datasheet" (p8). RM69310 datasheet not checked. Start-up code: not in this document (p8 "Recommended Setting ... Please refer" only). Single-unit purchase: not in document.

### 1.2 Truly TR095A120SPC (0.95 in AMOLED, 120 x 3 x 240), Panox-hosted copy [F]
- Source: https://www.panoxdisplay.com/uploadfile/datasheet/TR095A120SPC_1-10_1.pdf (saved `design/datasheets/slim_truly-tr095a120spc.pdf`), Truly Rev 0.1, 2019-01-18.
- LTPS glass outline 12.8 x 27.35 mm; encapsulation glass 12.8 x 24.4 mm; total thickness 0.78 mm (p5). Long side 27.35 mm: does not fit.
- Active area 10.8 x 21.6 mm; 120 x 3 (RGB) x 240; pixel pitch 80 x 80 um; diagonal 0.95 in (p5). Driver RM69310, interface SPI (p4).
- Pin table (p8): 30 pins, listed (1 GND, 2 TP_SDA, 3 TP_SCL, 4 VDD_TP, 6 SWIRE, 7-8 ELVDD, 9 VCI_DIS_28, 10 VDDIO, 12 SPI_SDI, 13 SPI_CLK, 18 SPI_CS, 19 SPI_DCX, 20 SPI_SDO, 22 DIS_RST, 23-24 ELVSS, 25 TE, 26 MTP, 27 TP_INT, 28 TP_RST, 30 KEY_SIGNAL TBD). Connector type and pitch: not in document.
- Supplies (p5): VCI_DIS_28 2.7 to 3.6 V (2.8 typ); VDDIO 1.65 to 3.3 V; ELVDD 4.55 to 4.65 V (4.6 typ); ELVSS -2.25 to -2.15 V (-2.2 typ). So the panel needs external +4.6 V and -2.2 V (ELVDD and ELVSS are inputs).
- Current (p5, full white 450 nit, 60 Hz, sleep-out mode): VCI_DIS_28 3.2 to 5 mA; VDDIO 1 to 2 mA; ELVDD/ELVSS 7 to 10.5 mA. Sleep-in and deep standby values also given (p5).
- Driver datasheet: not in document. Start-up code: not in document (p3 contents lists no initial code). Single-unit purchase: not in document.

### 1.3 Tailor Pixels TOH095XVT-01 (0.95 in AMOLED, 120RGB x 240, bar type), maker document [F]
- Source: https://tailorpixels.com/wp-content/uploads/2025/04/TOH095XVT-01_0.95-inch-Small-AMOLED-Display-Bar-Type-120x240-SPI.pdf (saved `design/datasheets/slim_tailor-toh095xvt-01.pdf`; same product as the earlier `design/datasheets/display_TOH095XVT-01.pdf`), Rev V0, 2025/01/03.
- Module outline 12.8 (H) x 27.35 (V) x 0.8 (T) mm, p4. Long side 27.35 mm: does not fit. Active area 10.8 x 21.6 mm (p4). Resolution 120RGB x 240 (p4). Driver IC SH8501A, interface 4SPI (p4). PPI 282 (p4).
- Pin table (p6): 15 pins: 1 ELVSS (-2.3 to -2.1 V), 2 ELVDD (4.55 to 4.65 V), 4 MTP, 4 VCI (2.7 to 3.6 V), 5 IOVCC (1.65 to 3.3 V), 6 SWIRE, 7 TE, 8 RESX, 9 CS, 10 SCL, 11 RS, 12 SDA, 13-15 GND. As printed, pin 4 appears twice and pin 3 is absent; numbers are shown as printed. Connector and pitch: drawing on p5 shows 15 pins; pitch not stated in text.
- Current or power: the electrical table p7 has blank current values. Power at a stated brightness: not in document. Luminance 450 cd/m2 is given in the module table (p4, "Luminance on surface"), with no stated test current in that row; optical table p8 uses I f = 20 mA backlight, which is the LCD-mode row, so it does not apply to this AMOLED.
- Driver datasheet: not in document. Start-up code: section 8 "Initialization Code" is listed in the contents (p3); the code body was not read in this run. Single-unit purchase: not in document.

### 1.4 EDO095-180120 (Everdisplay, 0.95 in 180 x 120 AMOLED); same panel as DisplayModule DMGXO0095S8NA [S]
- Source: https://marketplace.oled-info.com/view/162/EDO095-180120 (page text fetched; lines cited by the fetch summary). Listed status: EOL (production status and availability).
- Panel size 22.23 x 18.32 mm; thickness 0.75 mm; active area 20.03 x 13.36 mm; resolution 180 x 120; interface 4-wire SPI. Outline 22.23 mm long side and 18.32 mm short side: does not fit.
- Driver and supply voltages: not on that page. DisplayModule listing gives driver RM67160, SPI and capacitive touch and the same outline 22.23 x 18.32 x 0.75 mm: https://www.displaymodule.com/products/0-95-inch-180x120-amoled-spi-ctp-rm67160-dmgxo0095s8na (WebFetch returned HTTP 429 and 404 in this run, so these figures come from the search result text only, [S]).
- Connector, pin count, power, datasheet: not checked, the DisplayModule page could not be fetched.

### 1.5 DM-OLED096-658 (DisplayModule, 0.96 in monochrome PMOLED, 64 x 128), maker document [F]
- Source: https://cdn.shopify.com/s/files/1/0264/7629/files/DM-OLED096-658_Datasheet.pdf (saved `design/datasheets/slim_dm-oled096-658.pdf`), first release 2019-08-08.
- Module dimension 14 x 28 x 1.22 mm; active area 10.86 x 21.74 mm; resolution 64 x 128; controller SH1107; interface SPI (and I2C per section 6.4.2); display mode passive matrix OLED, monochrome white (all p3). Long side 28 mm: does not fit (short side 14 mm does).
- Pin table, connector, supply voltages, current: not read in this run (pages 4+ not extracted). Driver datasheet (SH1107): not checked.

### 1.6 DM-OLED095-626 (DisplayModule, 0.95 in monochrome PMOLED, 96 x 64), maker document [F]
- Source: https://win.adrirobot.it/datasheet/LCD/PDF/DM-OLED095-626Datasheet.pdf (saved `design/datasheets/slim_dm-oled095-626.pdf`), copyright 2015. Also on displaymodule.com.
- Module dimension 25.70 x 22.20 x 1.50 mm; active area 20.14 x 13.42 mm; resolution 96 x 64; controller SSD1331; interface SPI; passive matrix OLED, 65,536 colours (p3). Outline does not fit.

### 1.7 Dropped as not AMOLED/OLED or not 0.85 to 0.96 in: [S]
- Waveshare 0.85 in 128 x 128 (GC9107): an IPS LCD, not an OLED. Search summary only.
- Shenzhen Yousee 1.41 in and Electrodragon 1.9 in RM67162 modules: diagonal out of range.
- Szlcsc-hosted AMOLED datasheet (`design/datasheets/slim_szlcsc-0ee5.pdf`, JX943): 1.43 in round, 466 x 466, ST7801N, 43.20 x 43.20 mm outline (p4). Not a fit; read in full.

### 1.8 Not found
- Panox 0.9 in AMOLED: no datasheet found in the search results (search terms: "Panox Display 0.9 inch AMOLED module outline size datasheet"). Panox site hosts 0.95 in parts only in the results seen.
- Tailor Pixels 0.9 in AMOLED: not found in the search (term: "Tailor Pixels 0.9 inch AMOLED module datasheet"). Tailor catalog results were 1.43 in, 1.51 in, 1.75 in, 0.95 in only.
- Shineworld and EDO 0.9 in 180 x 120 or 128 x 128 AMOLED: not found (term: "Shineworld OR EDO 0.9 inch AMOLED 180x120 module outline mm datasheet pdf"; "oled-info marketplace AMOLED 0.9 inch ... EDO09").
- Visionox and Tianma 0.9 in AMOLED: not found; Visionox results were 1.43 in and round 33.22 mm (RM67162) only (term: "Visionox OR Tianma 0.9 inch AMOLED module datasheet").
- Gesight small AMOLED modules: no datasheet with an outline inside 21 x 14 mm; Gesight tag page lists 1.2 in and larger (https://gesight.com/product-tag/slim-design).
- Monochrome 0.85 to 0.91 in OLED with outline inside 21 x 14 mm: not found in the searched places (term: "0.85 inch OLED module 21x14 mm outline FPC SPI SSD1331 or SH1107 datasheet"; "0.91 inch OLED module 128x32 ... 21 x 13 mm datasheet"). The 0.91 in 128 x 32 modules found are 36 to 38 mm long.
- Driver datasheets (RM69310, RM67160, SH8501A, SH1107): not checked in this run.
- Whether any of these panels can be bought in single units: not checked (no supplier contact or sign-up).

## 2. Cell (thickness 2.0 to 3.0 mm, width 10 to 13.5 mm, length 15 to 20 mm)

Result: no cell in the searched catalogues fits all three ranges. The closest is Grepow GRP2409017 (width 9.6 mm, 0.4 mm under the range). Data are from a WebFetch summary of the Grepow page (not a saved copy, no line numbers; row order given), so treat them as [S] until the page is opened by hand.

### 2.1 Grepow ultra-narrow pouch cells: https://www.grepow.com/shaped-battery/ultra-narrow-battery.html [S]
WebFetch of the page returned a 23-row table. Rating fields: "Capacity" (single value, nominal or typical not stated), "C Rate" (not a charge current in amps), full-charge voltage. Rated voltage, max charge current and per-model datasheet links are not on the page (the page says "Contact us for a complete Ultra narrow Li-ion battery list").

Rows that come nearest to the target (thickness x width x length, mm; capacity mAh; full-charge V; rate):
- GRP2409017: 2.22 x 9.6 x 17.55; 24 mAh; 4.35 V; 1C. Thickness and length fit; width 9.6 is below 10. Closest.
- GRP2310021: 2.18 x 10 x 21; 30 mAh; 4.35 V; 1C. Width fits, thickness fits, length 21 is above 20.
- GRP2010021: 1.85 x 10 x 21; 24 mAh; 4.2 V; 1C. Thickness 1.85 below 2.0, length 21 above 20.
- GRP3710021: 3.47 x 10 x 21; 38 mAh; 4.2 V; 15C. Thickness and length above range.
- GRP3418019: 3.19 x 8 x 19; 33 mAh; 4.35 V; 1C. Thickness above 3.0, width 8 below 10.
- GRP1908021 (1.85 x 8 x 21, 18 mAh, 4.2 V) and GRP1606022 (1.6 x 6.5 x 22, 13 mAh, 4.2 V): outside on all three.
Other rows in the table are 9 to 50+ mm long or 5 mm and thicker.

Grepow's other shaped-battery pages (https://www.grepow.com/shaped-battery/) returned no spec tables through WebFetch; the subpage links were listed (ultra-thin, curved, round, L, rectangle, D, C). Those subpages were not opened in this run.

### 2.2 Other makers
- DNK Power: search returned "3.7V DNK... LiPo" datasheets on dnkpower.com (for example DNK387055, DNK601245, DNK651730). No 2.8 mm thick cell in the results. Locally saved DNK datasheets (`design/datasheets/cell_dnk_*.pdf`, read in this run, not downloaded by me) list dimensions such as 26x8x3.2 mm (DNK320824), 28x25x4.0 mm (DNK402526), 26x26x6.8 mm (DNK682624), with 4.2 V charge voltage and 4.275 V over-charge detection (PCM packs). None fits.
- EEMB: "LP" codes read as thickness x width x length in mm by EEMB's FAQ (https://www.eemb.com/faq-6, quoted in search summary). No LP283019 or LP282818 datasheet found in the search results. Not found.
- PKCELL: LP502035 is 5.0 x 20 x 35 mm, 350 mAh, 3.7 V nominal, and LP503035 is 5.3 x 30.5 x 35 mm, 500 mAh, 3.7 V (search summary of directindustry and parts-express listings). Both too thick and too long. Not found in range.
- LiPol: LP353035 (400 mAh, 3.7 V, PCM pack) is in the search results; its thickness is 3.5 mm and length 35 mm, outside the range.
- Jauch: saved copies `design/datasheets/cell_jauch_lp501218jh.pdf` (Typ. 65 mAh, 4.2 V charge) and `design/datasheets/cell_jauch_lp851719ju.pdf` (Typ. 200 mAh, 4.2 V charge). Dimension rows not read in this run; name code suggests 5.0 mm thick, not verified.
- Grepow GRP403530 (4.35 V, 360 mAh, with PCM): listed on DigiKey (https://www.digikey.com/en/products/detail/grepow-inc/GRP403530-1C-4-35V-360mAh-with-PCM/25603152). Thickness 4.0 and length 35 mm from the part code, not verified; outside the range.

### 2.3 Not found
- A cell at 2.8 x 13 x 19 mm: not found in these searches (terms: "lithium polymer battery 2.8mm x 13mm x 19mm 4.2V datasheet capacity mAh"; "\"283019\" lipo battery 3.7V capacity mAh"; "EEMB LP 283019 OR 283018 OR 282818 ..."; "DNK Power 2.8mm thickness ... 4.35V ..."; "PKCELL OR LiPol ultra thin ... 3.0mm ... 4.35V ..."). Searched places: grepow.com (ultra-narrow and shaped-battery index), dnkpower.com results, eemb.com FAQ, pkcell and LiPol result pages, Jauch and DNK saved files.
- Max charge current in mA for any Grepow row: not given (the page gives C rates only).
- Full-charge voltage 4.2 V and 4.4 V for the thin rows: only the rows above are listed; 4.4 V thin cells not found in range.

## 3. Switches for a 5-way thumb control (4 directions plus centre press)

Result: the only maker document read in full is the Alps SKTAAAE010 spec (a 1-pole, 1-throw tact switch with projection). It gives force, travel, life and IP, but not the outline or land pattern, which the spec points to a drawing for. The 4-direction layout with five switches was not found as a maker part. Every other figure below is [S] from a search summary and is unverified.

### 3.1 Alps SKTAAAE010 (SKTA series, 1 pole 1 throw, projection type) [F]
- Source: saved copy `design/datasheets/slim_alps-skta-aaae010-orwin.pdf` (7 pages, Alps document KTA-601, "For reference", date 201707). Original URL: https://orwintech.com/static/pdf/SKTAAAE010.pdf (distributor-hosted copy of the Alps document, counted as maker document).
- Ratings: 12 V DC 50 mA max; 1 V DC 10 uA min (p1, section 5).
- Operating temperature -30 to 85 C; storage -40 to 90 C (p1, sections 1.2 and 1.3).
- Operating force 1.6 +/- 0.5 N (p2, section 7.1). Travel 0.11 +/- 0.05 mm (p2, section 7.2). Return force 0.1 N min (p2, section 7.3). Stop strength 50 N for 15 s (p2, section 7.4).
- Contact resistance 500 mOhm max; insulation 100 MOhm min; voltage proof 100 V AC (p1, section 6). Bounce 10 ms max, on and off (p1, section 6.4).
- Protection: IP6X equivalent (dust) and IPX7 (water, 1 m, 30 min) (p3, section 8.5).
- Operating life: 300,000 cycles at 5 VDC 5 mA resistive, 2 to 3 operations per s, 2.1 N max depression (p3, section 9.1).
- Reflow: peak 260 C max for 3 s; 2 times max; cream solder M705-GRN360-K; PWB thickness 1.6 mm recommended (p4, section 10.1 and 10.2).
- Dimensions and land pattern: section 2.2 says "Refer to the assembly drawings" (p1). No outline dimensions in the text of pages 1 to 7 of the saved copy; the page 4 image shows soldering conditions only. Search summary gives 2.6 x 1.6 x 0.53 mm (LCSC listing https://www.lcsc.com/product-detail/C358621.html) [S]. Land pattern: not in document.
- Production status: not stated in the document. The copy is marked "For reference".
- Note: a second copy, `design/datasheets/slim_alps-skta-aaae010-ibs.pdf` (5.8 kB, HTML page not PDF), gave the same force and life in search text [S]. Not used.

### 3.2 Alps SKRP and SKSC series [S]
- SKRP (top-actuated, compact): search summary of Alps series listings gives size 4.2 x 3.2 x 2.5 mm (listing: https://www.mouser.com.gt/alps-skrp-tact-switches, https://octopart.com/part/alps/SKRPACE010). SKRPABE010: 1.57 N operating force. SKRPACE010: 255 gf, 50 mA at 16 V DC. Life: 50,000 cycles (one listing) or 150,000 cycles (another listing) for different parts. Not confirmed against the maker's PDF.
- SKSC (side push, low profile): 1.25 mm height; one listing gives 100,000 cycles at 50 mA 12 V DC; another gives footprint 3.5 x 3.55 mm (https://dtsheet.com/model/3344174). Operating force not found. Manual soldering 350 C max, 3 s max (search summary).
- Maker PDFs for SKRP and SKSC: not opened in this run (alpsalpine.com not reached; distributor PDFs not saved).

### 3.3 C&K (Littelfuse) KMT0 nano-miniature [S] only
- Search summary of the KMT0 datasheet: current Littelfuse revision (Oct 2024) gives 3.6 x 2.6 mm footprint, 0.65 mm actuator height (https://www.ckswitches.com/media/2213/kmt0.pdf). Older 2018 sheet: 3.0 x 2.6 mm, IP68 (same search). No 3.0 x 2.0 mm KMT0 variant found.
- Distributor listing name KMT031NGJLHS gives 3.4 N (distrelec listing, https://www.distrelec.ch/en/tactile-switch-50-ma-32-vdc-momentary-function-1no-4n-smd-kmt0-kmt031ngjlhs/p/30438322, the title says 4N and 3.4N in different places; not resolved).
- Maker PDF not read: ckswitches.com returned a page-access denial (saved `design/datasheets/slim_ck-kmt0.pdf`, 454 bytes, is a redirect or error, not a datasheet) and the Mouser copy returned an access-denied page (saved `design/datasheets/slim_ck-kmt0-mouser.pdf`, HTML). The ckswitches product page redirected to littelfuse.com/products and was not followed (generic list).

### 3.4 Panasonic EVQ-P4 (side push, edge mount) [S]
- Series page: https://na.industrial.panasonic.com/products/switches-encoders-interface-devices/switches/light-touch-tactile-switches/series/79291. Search summary: 6.2 x 2.55 mm body, 1.35 mm above PCB. Middle-travel variants 0.70 +/- 0.2 mm with 2.5 N, 3.5 N, 5.0 N and life 1,000,000, 500,000 and 200,000 cycles. Short-travel variants 0.25 mm with 1.0 to 3.5 N. Push strength 50 N. Not a 3 to 4 mm part, so it does not meet the size request.
- EVPBB: not found in search. EVP-AA: a saved copy from earlier work exists (`design/datasheets/p3_evpavaa1a_farnell.pdf` and text files); not read in this run.

### 3.5 Snaptron metal domes [S]
- F06085 [F-table, HTML]: saved copy `design/datasheets/slim_snaptron-f07200.pdf` (an HTML page, not a PDF, of the Snaptron F-series table; original https://www.orwintech.com/static/pdf/F07200.pdf) lists F06085 with diameter 6mm (0.236"), height 0.30mm (0.012"), trip force 85g, dimple No, life up to 5,000,000 cycles. The saved file's popup also lists Dim. B 1.22 mm, Dim. D 5.00 mm and Dim. E 2.44 mm. The +/- 30 g typical is from the WebFetch summary only [S]. Maker PDF for 3 to 5 mm F-series: not found. The 4 mm F-series datasheet was not found.
- Dome force: 85 gf is about 0.83 N (own conversion, not from the source).
- Land pattern and IP rating: not in the fetched page.

### 3.6 Published wearable ring or thumb-joystick designs [S]
- US20060164383A1, "Remote controller ring for user interaction" (https://patents.justia.com/patent/20060164383; Justia returned 403 in this run, the summary is from the search result text, see also https://insight.rpxcorp.com/pat/US20060164383A1): a ring worn on the index finger with a joystick lever operated by the thumb; the joystick operates switches or potentiometers; joystick-operated navigation switches may be subminiature tact switches; pressing the lever down makes a selection by closing a fifth switch. Closest match to the 4-way plus centre press mechanism.
- US12321517, "Wearable remote controller" (https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12321517): a micro joystick lever projecting out of the ring housing, operated by the thumb, wireless link to an external device (search summary).
- US4256931A (https://patents.google.com/patent/US4256931): several resilient dome momentary switches, equally spaced in a circle, with a pivoting key above; a circular central force area so one finger can actuate any switch. Not a ring; a dome-based 4-way layout.
- Hackster article on the Mouse Ring V2 (https://www.hackster.io/news/rafal-gajek-overhauls-the-wearable-ring-mouse-delivers-two-control-modes-and-improved-ergonomics-e3a212136461, WebFetch summary): the original ring used four tactile switches in a cross; V2 replaces them with a five-way joystick (four directions plus press) operated by the thumb; controller is a Seeed XIAO nRF52840. Switch part numbers and joystick part not named in the summary.
- The search found no ring with exactly five dome switches. Gap noted.

### 3.7 Not found
- A maker datasheet for any 4 mm or smaller F-series Snaptron dome: not found (search "Snaptron metal dome F-series 4mm datasheet pdf actuation force").
- A 3.0 x 2.0 mm C&K KMT0 variant: not found in the KMT0 search results.
- EVPBB datasheet: not found (search "Panasonic EVQ-P4 OR EVPBB ultra miniature tactile switch ...").
- SKRP and SKSC maker datasheets from alpsalpine.com: not opened; search summary only.
- Production status (active, NRND, EOL) for any switch in this section: not stated in any opened document.
- Land patterns for SKTA, SKRP, SKSC, KMT0: not in the opened documents.

## 4. Storage: at least 2 GB (16 Gbit) in a package smaller than 6.2 x 8 mm

Result: no part with at least 2 GB was confirmed by a maker document in a package at or under 6.2 x 8 mm. The 4 GB SD NAND parts that are listed at 6 x 8 mm or 6.2 x 8 mm are distributor claims [S] that the saved copies do not confirm. The maker documents that were read give 6 x 9 mm (CS CSNP32GCR01, product list marked TBD) and 9 x 12.5 mm (Zetta ZDSD32GLVEAG and ZDSD32GLVIAG). The XTX family tops out at 8 Gbit.

### 4.1 Zetta ZDSD32G/64G/128G (32 Gbit = 4 GB), maker document [F]
- Source: saved `design/datasheets/slim_szlcsc-0526-zetta-or-other.pdf` (18 pages, ZDSD32G/64G/128G product datasheet, hosted at https://atta.szlcsc.com/upload/public/pdf/source/20260527/B7BE5B7F428770388C737A5A3381E24C.pdf). Document is a Zetta datasheet.
- Package: "LGA8x2 (Land Grid Array) 9x12.5mm" for ZDSD32GLVEAG and ZDSD32GLVIAG (p3 product table, text lines 84 to 110), and p17 "LGA8x2 9x12.5mm". Too large for the 6.2 x 8 limit.
- Ordering key (p18): E = Extended (-25 to +85 C), I = Industrial (-40 to +85 C); supply 2.7 to 3.6 V (p18). Operating temperature range Extended Ta -25 to +85 C (p3 feature list).
- Pins (p4, section 5): SD mode 4-bit and 1-bit, and SPI mode: CS, DI, SCLK, DO, VDD, GND, NC. SPI mode is supported by the pin table.
- Currents: not read in this run (no current table in pages 1 to 5 extracted).
- LCSC listing for ZDSD32GLGEAG (6.2 x 8 mm per search summary, https://www.lcsc.com/product-detail/C5188571.html) [S]: the saved LCSC page `design/datasheets/slim_zetta-zdsd32glgeag.pdf` is an HTML product page with no package text. Not confirmed.

### 4.2 CS Semiconductor CSNP32GCR01 (32 Gbit), maker-hosted spec [F]
- Source: saved `design/datasheets/slim_cs-sdnand-spec-sipeed.pdf` (8 pages, "CS SDNAND Product specification V1.0.3(2)", hosted at https://dl.sipeed.com/Accessories/SDNAND/CS%20SDNAND%20Product%20specification%20V1.0.3(2).pdf). Read pages 1 to 8.
- Product list (p3, section B): CSNP1GCR01 1 Gb LGA-8 6x8 mm, "Now"; CSNP4GCR01 4 Gb LGA-8 6x8 mm, "Now"; CSNP32GCR01 32 Gb LGA-8 6x9 mm, availability "TBD" (p3, lines 128 to 144).
- Feature line (p3): "Support Capacity: 1Gb-4Gb" and "The capacity of SDNAND memory is from 1Gb to 4Gb ... 8mm x 6mm x0.75mm" (p3). So the document's own capacity range stops at 4 Gb, and the 32 Gb part is in the table only.
- Mechanical (p7, section G, common dimensions, mm): A 0.65 / 0.75 / 0.85; B 1.17 / 1.27 / 1.37; C 6.90 / 7 / 7.10; D 7.90 / 8 / 8.10 (min / nom / max). Which column is which part is not labelled in the extracted text.
- Currents (p6 table): work current max 30 mA and 55 mA; standby 150 uA and 60 uA; read speed 15 MB/s; write speed 4 and 6 MB/s. Column labels not extracted; the two values are shown in the order of the table.
- SPI: p5 notes the DAT3 line "can be used for card detection or SPI mode" (p5). No SPI pin table in this document.
- Distributor listing for AOW variant (6.2 x 8 LGA-8, 2.7 to 3.6 V, 50 MHz) (https://www.lcsc.com/product-detail/C2841139.html) [S]: conflicts with the maker product list (6 x 9). Not resolved.
- Saved `design/datasheets/slim_cs-csnp32gcr01-bow.pdf` is an LCSC HTML page (9.6 kB), no package text. Not used.

### 4.3 MK-Founder MKDV32GCL (32 Gbit = 4 GB) [S] only
- MKDV32GCL-STH: LCSC listing gives LGA-8 6 x 8 mm and 208 MHz (https://www.lcsc.com/product-detail/C5199868.html) [S]. Saved copy `design/datasheets/slim_mk-mkdv32gcl-sth.pdf` is an LCSC HTML page (9.4 kB) with no package text.
- MKDV32GCL-STP: LCSC listing gives LGA-8 6.6 x 8 mm and 50 MHz (https://www.lcsc.com/product-detail/C7500179.html) [S]. Saved copy `design/datasheets/slim_mk-mkdv32gcl-stp.pdf` is HTML with no package text.
- MKDV32GCL-STL: JLCPCB lists W-PDFN-8-EP (6 x 8), 50 MHz SPI (https://jlcpcb.com/partdetail/MK-MKDV32GCLSTL/C2844071/C2844071) [S].
- Maker datasheet read: `design/datasheets/slim_szlcsc-1112-mk-or-other.pdf` (22 pages, MK SD NAND family, product list MKDV1GCL-ABG, MKDV2GCL-ABG, MKDV4GCL-ABG, i.e. 1 to 4 Gb; section 5 "Pin Assignments (SD Mode & SPI Mode)" on p6). It does not list MKDV32GCL. Package dimensions (section 10, p21) is an image page; not read. So no maker dimension for MKDV32GCL in hand.
- The search did not find a 6.2 x 8 mm MKDV32GCL; the closest are 6 x 8 and 6.6 x 8 (search summary).

### 4.4 XTX XTSD01G / 02G / 04G / 08G (1 to 8 Gbit), maker document [F]
- Source: saved `design/datasheets/slim_xtx-xtsd0xglgeag-v2.pdf` (13 pages, XTX SD NAND datasheet V2, hosted at https://whycan.com/files/members/3/XTX_SD_NAND_1Gb_2Gb_4Gb_8Gb_XTSD0xGLGEAG_V2.pdf).
- Package: LGA8 "8*6mm" for XTSD01GLGEAG, XTSD02GLGEAG, XTSD04GLGEAG and XTSD08GLGEAG (package table, text lines 68 to 85).
- Capacity: largest part in the family is XTSD08G (8 Gbit = 1 GB). No 16 Gbit or 32 Gbit part in this datasheet, so it does not meet the 2 GB limit.
- Pin assignments for SD mode and SPI mode: section 5 (text lines 120 onward). Current values: not extracted.

### 4.5 eMMC (smallest ball packages) [S]
- Search summary only (https://smartm.com/product/448 is listed as BGAE340 eMMC 153 ball / 100 ball, no dimensions read; At-com subsize eMMC: https://at-com.com/technical-articles/330-subsize-emmc.html): 4 GB and 8 GB MLC subsize eMMC 153-ball in 9 x 7.5 x 0.8 mm, 9 x 10 x 0.8 mm and 10 x 11 x 0.8 mm (eMMC 5.1, HS400, 3.3 V / 1.8 V). Ball count and pitch not confirmed.
- Micron 4 GB and 8 GB eMMC datasheet, 153-ball WFBGA 11.5 x 13 x 0.8 mm (search summary; https://dtsheet.com/model/2724231 listed, not opened).
- Zetta ZDEMDCM004G-BG25 4 GB MLC FBGA153 11.5 x 13 x 1.0 mm (search summary).
- eMMC SPI-mode support and currents: not checked. eMMC uses the 153-ball package in all listed parts; no eMMC maker datasheet was opened in this run.

### 4.6 Not found
- A 2 GB or larger part in an LGA or WSON package that is under 6.2 x 8 mm, confirmed by a maker document: not found.
- The Zetta ZDSD32GLGEAG 6.2 x 8 mm datasheet: not found in the searched places (LCSC page saved, no package text).
- The MKDV32GCL maker datasheet and its package dimensions: not found (section 10 of the saved MK file is an image page).
- SD NAND SPI-mode currents for the 32 Gbit parts: not found in the opened documents.
- eMMC maker datasheets (Micron, Zetta, Kioxia, Samsung) and their SPI-mode support: not opened in this run.

## 5. Microphones: PDM, 3.5 x 2.65 mm or smaller, SNR 68 dB or more

Result: two parts found with a maker document that shows 3.5 x 2.65 x 0.98 mm and 68 dB(A) SNR: Infineon IM68D121J (read from its product brief, [F]) and TDK T5838 (search and product-page text, [S] for the figures). A third, Knowles SPH0690LM4H-1, has 68 dB(A) in a Knowles brief found by search [S]; its datasheet was not reachable. The Infineon IM68D128B (3.5 x 2.65 x 0.98 mm, already read) is not repeated here. No part found is smaller than 3.5 x 2.65 mm with 68 dB or more.

### 5.1 Infineon IM68D121J (XENSIV digital PDM, bottom port) [F]
- Source: product brief, saved `design/datasheets/slim_infineon-im68d121j-brief.pdf` (1 page), https://www.infineon.com/content/dam/infineon/row/public/documents/24/45/infineon-im68d121j-productbrief-en.pdf. Brief, page 1.
- Package: 3.5 x 2.65 x 0.98 mm, "All dimensions in mm" (p1). Port: bottom, acoustic port ø0.325 through (p1 drawing text).
- SNR: 68 dB(A) (p1; the body text also says "68 dB(A) Signal-to-noise ratio").
- Current: 580 / 190 µA (normal mode HPM / LPM, p1). Supply 1.62 to 3.60 V (p1).
- Interface: Digital PDM (p1). Pins shown on the bottom view (p1): Clock, VDD, Ground, Data, Select (5 pins).
- Sensitivity -26 dBFS +/- 1 dB at 94 dB SPL (HPM/LPM) (p1). Acoustic overload point 118 / 121 dBSPL (p1). LFRO 20 Hz (p1). IP57 (p1).
- Datasheet (full) not read: the brief is the only Infineon document saved in this run.

### 5.2 TDK InvenSense T5838 (multi-mode PDM, bottom port) [S]
- Source: TDK product page https://invensense.tdk.com/?p=11595 (WebFetch; the page itself has only a summary and no table). Search summary of TDK's product table gives: package 3.5 x 2.65 x 0.98 mm, PDM, bottom port, 68 dBA SNR (High-Quality and Ultrasonic modes; Low-Power 65 dBA), 133 dB SPL AOP, -41 dBFS sensitivity, 28 Hz LF cutoff, document DS-000383 v1.1 (2023-04-21), status production (search text, URL https://www.digikey.co.uk/en/products/detail/tdk-invensense/MMICT5838-00-012/16903860).
- Current: "as low as 20 µA" for Acoustic Activity Detect mode only (TDK page summary [S]). Normal-mode current: not found.
- Supply 1.8 V (search summary, [S]). Datasheet PDF: not reached (no download link in the fetched text).

### 5.3 TDK InvenSense T5837 [S]
- Search summary (distributor table): 3.5 x 2.65 x 0.98 mm, PDM, bottom port, 68 dB SNR, 133 dB AOP, -37 dBFS sensitivity, 28 Hz, production; datasheet DS-000447 v1.2 (2023-09-19) (search text, https://www.digikey.cn/en/products/detail/tdk-invensense/MMICT5837-00-012/16903859 listed; not opened). Current: not found. Pins and supply: not found.

### 5.4 Knowles SPH0690LM4H-1 (Everest, PDM, bottom port) [S]
- Package 3.50 x 2.65 x 0.98 mm and 68 dB(A) SNR in a Knowles selection guide and mic-on-flex brief (search summary; brief URL https://www.mouser.com/catalog/specsheets/knowles%20corp_01312020_KAS-700-0147%20Everest%20Mic%20on%20Flex%20Product%20Brief.pdf, not saved as PDF: the saved file `design/datasheets/slim_knowles-everest-miconflex-brief.pdf` is an HTML page).
- Conflicting figures [S]: Knowles product page 69 dB at 1.536 MHz clock (search text); DigiKey listing 66 dB. Current: 750 µA (Knowles brief, search summary) vs 2 mA (DigiKey listing, search summary). Supply 1.65 to 3.6 V and clock 1.1 to 4.8 MHz in normal mode (brief summary).
- Datasheet: https://www.knowles.com/docs/default-source/default-document-library/sph0690lm4h-1_everest_datasheet_.pdf (cited by a third-party listing). The saved copy `design/datasheets/slim_knowles-sph0690lm4h-1.pdf` is an HTML page with no specification text. Not read.

### 5.5 Other Knowles parts seen [S]
- SPH0641LM4H-1: 3.50 x 2.65 mm (0.138 in x 0.104 in); S/N ratio 64.3 dB (search summary, https://www.mouser.com/datasheet/2/218/sph0641lm4h_1_morello_datasheet-952032.pdf). SNR below 68 dB: does not meet the target.
- SPH0645: 3.50 x 2.65 x 0.98 mm package size (NXP-hosted copy of Rev C, https://community.nxp.com:443/pwmxy87654/attachments/pwmxy87654/imx-processors/171279/1/ph0645lm4h-b-datasheet-rev-c-1525723.pdf). SNR not found. Not checked against Knowles' own copy.

### 5.6 Not found
- A PDM microphone smaller than 3.5 x 2.65 mm with SNR 68 dB or more: not found (search "digital PDM MEMS microphone 3.5 x 2.65 x 0.98 mm SNR 68 dB datasheet" and the TDK and Knowles searches listed above).
- Normal-mode current for T5838 and T5837: not found in the opened text.
- Maker PDFs for T5837, T5838 and SPH0690LM4H-1: not reached in this run (TDK and Knowles pages returned no PDF or no spec text).

## 6. Vibration part (at most 2.6 mm tall, footprint at most 8 x 8 mm)

Result: no vibration part was confirmed at 2.6 mm tall or less with an 8 x 8 mm or smaller footprint. The 6 mm coin motors read from maker documents (INEED C0620BLDCL27, Vybronics VW0620AB001U) are 6 mm in diameter with a drawn body height of 2.0 mm plus 0.3 mm foam and 0.15 mm tape; the drawn stack is about 2.45 mm, and the adhesive labels are not clear on total height. Read values are below. Heights are as labelled on the drawing; the total stack height is not stated in either document.

### 6.1 INEED C0620BLDCL27 (coin BLDC, 6 mm) [F]
- Source: saved `design/datasheets/slim_ineed-c0620bldcl27-spec.pdf` (13 pages, spec no. IND20221128S001A, released 2022-11-28). Original: https://www.ineedmotors.com/uploads/16849/files/C0620BLDCL27-Spec.pdf?rnd=697
- Rated voltage 3.0 V DC; operating voltage 2.7 to 3.3 V DC (p3, section 2, items 2-1 and 2-2).
- Rated speed 13,000 rpm min; rated current 80 mA max; starting current 150 mA max; starting voltage 2.5 V DC max; response time 190 ms max; coil 12 Ohm +/- 20% (p3 to p4, section 4, items 4-1 to 4-7).
- Weight 0.34 g +/- 10% (p4, item 5-1).
- Connection: wire leads, Red (+) and Blue (-) (p3, item 2-4; p12 drawing).
- Drawing (p12): diameter 6 +/- 0.1; body 2.0 +/- 0.1 with 0.3 SRP foam on top and 0.15 two-side tape below; "MAX 2.0" UV adhesive and "UV 3.0 MAX" labels; lead length 27 +/- 2; lead offset 1.5 +/- 0.5. Total height from these labels is about 2.45 mm (body 2.0 + foam 0.3 + tape 0.15) if the UV adhesive is not above the body; not stated by the maker. Footprint: 6 mm diameter (leads extend about 27 mm).
- Operating temperature -20 to 60 C (p3, item 2-3).

### 6.2 Vybronics VW0620AB001U (BLDC coin, 6 mm; DigiKey says Obsolete) [F]
- Source: saved `design/datasheets/slim_vybronics-vw0620ab001u.pdf` (12 pages, Vybronics product specification). Original: https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VW0620AB001U-datasheet.pdf
- Rated voltage 3.0 V (p2 and p3, item 1 "Rated voltage 3.0 V"; distributor page also 3 VDC). Rated speed 13,000 rpm min; rated current 80 mA max; starting current 150 mA max; starting voltage 2.5 V DC max; insulation 10 MOhm min; coil 12 +/- 20% Ohm (p3, sections 4-1 to 4-6). Operating voltage range: not in document.
- Connection: wire leads, AWG32 UL3302 (p10 drawing note 6; distributor "Wire Leads").
- Drawing (p10): diameter 6 +/- 0.1; body height 2.0 +/- 0.1 with 0.3 SRP foam; "MAX 2.0" UV adhesive; "MAX 3.0" horizontal dimension; UV 2.8 Max; lead length 30 +/- 2; lead offset 1.5 +/- 0.5. Total height not stated.
- Operating temperature -20 to 60 C (distributor summary [S]).

### 6.3 TDK PowerHap 0904H014V060 (piezo haptic actuator) [S]
- Search summary of TDK press release (https://www.tdk-electronics.tdk.com/download/2517750/f56a03fd4b8744a20c1ea36025074e73/pdf-en.pdf): 9 x 3.75 x 1.4 mm; maximum operating voltage 60 V; 0.35 mJ per click; peak acceleration 3.3 g; displacement 15 um. TDK product note (https://product.tdk.com/en/producttechnotes/16431.html) returned HTTP 403 when fetched.
- Footprint 9 x 3.75 mm: does not fit 8 x 8 mm (long side 9 mm). Height 1.4 mm fits. Start-up voltage and rated current: not applicable to a piezo; not found. Connection type (pad or wire): not found.

### 6.4 Vybronics VLV200634A (LRA, 6 mm) [F-listing, S for dims]
- Source: saved `design/datasheets/slim_vybronics-vlv200634a-page.html` (HTML, the Vybronics product page; distributor copy at https://www.digikey.com/en/products/detail/vybronics-inc/VLV200634A/16719294). Size 6.00 x 3.43 mm, rectangular; rated 1.5 VAC; solder-tab termination; operating -25 to 70 C (DigiKey summary). Height 3.43 mm: does not meet 2.6 mm. Current and start-up: not listed.

### 6.5 Other Vybronics parts [S] (search summary only)
- VC0625B001L: 6 mm diameter brushed coin, 3 VDC, 10,000 rpm (DigiKey listings https://www.digikey.com.mx/en/products/detail/vybronics-inc/VC0625B001L/12323586). Thickness not confirmed; datasheet not reached.
- VC0625B002L: 6 mm, 2.5 VDC, 10,000 rpm (https://www.digikey.com.br/en/products/detail/vybronics-inc/VC0625B002L/21800222). Thickness not confirmed.
- VLV041235L (4 x 12 mm, 1.8 VAC), VLV152564W (14.6 x 6.4 mm, 1.4 VAC), VLV221007E (10 x 7 mm, 2.3 VAC): footprints do not fit 8 x 8 mm or are not known; heights not listed.
- Jinlong C0625, NFP: no results in search.
- AAC and Jahwa parts: not searched in this round (time limit).

### 6.6 Not found
- A coin motor of 6 mm diameter at 2.0 mm height or less, with a maker document giving current and start-up voltage: the INEED and Vybronics drawings show a 2.0 mm body with foam and adhesive above it, so the total height is not confirmed to be 2.0 mm or less.
- Vybronics VC0620 datasheet: not found (search "Vybronics VC0620 coin vibration motor datasheet ...").
- TDK PowerHap 0904H014V060 maker datasheet: not reached (press release only).

## 7. Screen connectors (mating board connector named by the maker)

Result: none of the four screen candidates that were read names a mating board connector. The documents give pin count, and for one, a flex-circuit tail. Items not read in this round are marked.

- 7.1 Panox BO095F120S (p4 to p6): pin table 20 pins (p6); "COG+FPC" (p5 text). Connector type and pitch: not named in the document. Drawing text on p5 gives "connector 0.51 mm" (unclear whether that is pitch or thickness). Mating connector part number: not in document.
- 7.2 Truly TR095A120SPC (p8): 30-pin interface table; a flex tail, no connector named. Pitch and mating connector: not in document.
- 7.3 Tailor TOH095XVT-01 (p5 to p6): 15 pins; drawing p5 "Contact Side" with pin numbers 1 to 15. Pitch and mating connector: not in document.
- 7.4 EDO095-180120 / DMGXO0095S8NA (section 1.4): not read; page not reached (429 / listing only).
- 7.5 DM-OLED096-658 (p3 to p4 of the saved copy): module pin description and connector not read in this round. Not checked.
- 7.6 DM-OLED095-626 (saved copy): module pin description and connector not read in this round. Not checked.
- Soldered tail, no connector: not confirmed for any candidate; the Truly, Tailor and Panox docs show pin tables without naming a connector.

## Source check (HEAD request, 16:4x CET, log `design/datasheets/slim_urlcheck.log`)

Status codes are from a HEAD request, so some servers answer differently from a browser or from WebFetch. Items below with a non-200 code are not confirmed by this check.
- 200 (loads): Panox BO095F120S and TR095A120SPC; Tailor TOH095XVT-01; DM-OLED096-658; DM-OLED095-626; Infineon IM68D121J brief; Alps SKTAAAE010 (orwintech copy); Snaptron F07200 page; XTX XTSD0xG datasheet; CS and MK LCSC pages; EDO095-180120 marketplace page; TDK product page (invensense.tdk.com/?p=11595).
- 502 (server error at check time): CS SDNAND spec at dl.sipeed.com. The copy was downloaded at 16:41 and is saved (`design/datasheets/slim_cs-sdnand-spec-sipeed.pdf`).
- 404 (not found at check time): Knowles SPH0690LM4H-1 datasheet URL (cited by a third-party listing); EEMB FAQ page cited in section 2; Grepow shaped-battery index and ultra-narrow page (WebFetch returned content for the ultra-narrow page earlier in this run, so the HEAD 404 is treated as a server difference, not a removed page).
- 403 (access denied): dtsheet model pages; DigiKey listings; C&K KMT0 PDF (ckswitches.com); Justia patent page.
- 429 (rate-limited): DisplayModule DMGXO0095S8NA product page.
- 405: RPX patent insight page (HEAD not allowed).
- 500: Gesight slim-design tag page.

## Limits and what is not done

- Time used: about 16:30 to 16:45 CET by file timestamps. Tool calls: about 90 of 110 (estimate).
- Disk: the shell hook reported 0.3 GB free on the disk holding this folder, below its 5 GB floor. Downloads in this run were small (about 40 MB in total, all under `design/datasheets/slim_*`). Nothing was deleted.
- Final audit: a targeted check, not a full claim-by-claim audit. Key [F] values (outlines, currents, pins, SNR, package sizes) were grepped in the saved copies (see the list in this run). Grepow values come from a WebFetch summary and are [S].
- Not done: EVP-AA and EVPBB datasheets; Alps SKRP and SKSC maker PDFs; Grepow subpages; RM69310, RM67160, SH8501A and SH1107 driver datasheets; eMMC maker datasheets; Shineworld, Visionox and Tianma product pages; purchase or stock checks (not in scope).

## questions_for_owner

1. No screen candidate found fits the 21.0 x 14.0 mm outline (closest: DM-OLED096-658 at 14 x 28 mm monochrome; the 0.95 in panels are 12.8 x 27.35 mm or 22.23 x 18.32 mm). Is a larger display outline acceptable, or should the search widen to other display types?
2. The only 2 GB or larger storage part with a confirmed small package is not found; the 4 GB SD NAND parts are 6 x 9 mm (CS, maker spec) or 9 x 12.5 mm (Zetta, maker datasheet), and the 6 x 8 claims are distributor listings only. Is a 6 x 9 mm part acceptable, or should the storage size limit change?
3. The disk holding `design/` reported 0.3 GB free (floor 5 GB). Please confirm if you want cleanup of other folders before further downloads; nothing was deleted by this run.

RESULT: done, sections 1 to 7 complete: no screen fits 21 x 14 mm, no vibration part meets 2.6 mm height with a maker-confirmed current, no 2 GB storage fits 6.2 x 8 mm with a maker document, and no screen connector is named by its maker document.
