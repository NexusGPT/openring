# Slim ring parts, round 2: maker datasheet facts

Date of the look: 2026-11-10 (CET). Files cited are saved copies in `design/datasheets/`. "pN" is the PDF page number of the saved copy. [F] = read from a maker document (a maker-hosted copy, or a spec issued by the maker and hosted by a third party, as noted). [S] = search text only.

## 1. Vibration part (at most 2.7 mm smallest dimension, at most 8 mm in the other two)

Result: five parts fit the size test on their drawings and have a maker document read by me. The deciding height is the drawn body height, not a stack height; none of the makers states a total height with adhesive and tape. Two of the five (Jinlong) are hosted on a third-party file host, noted per row.

### 1.1 Vybronics VC0625B001L (coin, brushed, 6 mm) [F]
- Source: https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC0625B001L-datasheet.pdf (saved as `slim2_vybronics-vc0625b001l.pdf`, 11 pages, spec rev A/3, 2021.09.09).
- Size: diameter 6 ±0.1; height 2.5 ±0.1 (p9 drawing, dimension labels read from the rendered page). The 10 ±2 and 4.6 callouts are the lead dimensions on the drawing (p9); the text layer does not name them.
- Rated voltage: 2.5 V DC (p3, 2-1). Operating voltage: 2.0 to 3.5 V DC (p3, 2-2).
- Rated speed: 10000 rpm min at rated voltage (p3, 4-1). Rated current: 100 mA max (p3, 4-2).
- Starting voltage: 2.0 V DC max (p4, 4-3). Starting current: not in the document.
- Vibration: "Grms 0.3 Min, Gp 0.4 Min", test with 50 g jig, rated voltage 2.5 V (p4, 5-3). Mechanical noise 50 dB max (p4, 5-3).
- Connection: tinned lead wires UL3302 AWG32; "+" red, "-" blue (p9).
- Life: 100,000 cycles, 1 s on, 1 s off, at 2.5 V (p5, 7-1).
- Terminal resistance: 12 ±20 Ohm in parallel (p4, 4-5).

### 1.2 Vybronics VC0625B002L (coin, brushed, 6 mm) [F]
- Source: https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC0625B002L-datasheet.pdf (saved as `slim2_vybronics-vc0625b002l.pdf`, 11 pages, dated 2023.08.03). The page 1 text layer is garbled; pages 2 to 4 and 9 are readable.
- Size: diameter 6 ±0.1; height 2.5 ±0.1 (p9 drawing). Drawing adds "Double-sided tape (Ø5.0, T0.15)" under the body (p9 drawing, rendered image).
- Rated voltage 2.5 V DC (p3, 2-1). Operating 2.0 to 3.5 V DC (p3, 2-2). Rated speed 10000 rpm min (p3, 4-1). Rated current 100 mA max (p3, 4-2). Starting voltage 2.0 V DC max (p4, 4-3). Starting current: not in the document.
- Vibration: "Grms 0.3 Min, Gp 0.4 Min" (p4, 5-3). Noise 50 dB max (p4, 5-3).
- Connection: lead wires UL3302 AWG32, "+" red, "-" blue (p9 drawing).
- Life: not in pages I read (p5 not read for this part).

### 1.3 Vybronics VC0720B088L (coin, brushed, 7 mm, FPC tail) [F]
- Source: https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC0720B088L-datasheet.pdf (saved as `slim2_vybronics-vc0720b088l.pdf`, 15 pages; cover date printed as 2026.09.01).
- Size: "Φ07, 2.0t" (p4, size spec line). Outside drawing (p13, rendered): ø7 ±0.1; height 2.1 ±0.1 including "0.15 FPC + 0.1 glue" and UV adhesive; double-sided tape T0.15 under the body; tail width 6.2 ±0.3 (p13 drawing).
- Rated voltage: DC 3.0 V (p4, 2-1). Operating voltage: DC 2.5 to 3.7 V (p4, 2-2).
- Rated speed: 8000 rpm min at 3.0 V (p5, 4-1). Rated current: 85 mA max (p5, 4-2).
- Starting voltage: 2.3 V max (p5, 4-3). Starting current: 120 mA max at 2.3 V (p5, 4-5).
- Vibration: 0.1 Grms min, 0.15 Gp min at 3.0 V, 75 g and 100 g jig set-ups (p6, 5-1). Noise 50 dB max (p6, 5-2).
- Connection: flexible printed circuit (FPC) tail, not wire leads (p13 drawing; BOM line 10 "FPCB", p14).
- Life: 50,000 cycles, 1 s on, 1 s off, at DC 3.0 V, normal temperature and humidity (p9, section 7).

### 1.4 Jinlong W0525AB001D (BLDC coin, Φ5 x 2.5 T) [F, third-party host]
- Source: Jinlong spec S-525113 rev 0 (2019.03.14), hosted at https://file.aichiplink.com/r/datasheets/jinlongmachineryelectronicsinc-w0525ab001d-datasheets-1013.pdf (saved as `slim2_jinlong-w0525ab001d.pdf`, 14 pages). The host is a third party; the document names Jinlong as the maker.
- Size: "Φ5x2.5T" (p2); diameter Ø5 ±0.05 and product height 2.5 ±0.1 (p4, CTF table). Weight 0.32 g ±10% (p6, 3-2-3).
- Rated voltage: DC 3.0 V (p6, 3-1-1). Operating voltage range 2.7 to 3.3 V (p5, 2-3-1).
- Rated speed: 14,000 ±3,000 rpm (p6, 3-1-3). Rated current: below 80 mA (p6, 3-1-4).
- Starting current: below 175 mA, measured with rotor held at operating voltage (p6, 3-1-5). Starting voltage: below DC 2.5 V (p6, 3-1-6).
- Vibration: 0.25 G (avg) (p6, 3-2-1). Mechanical noise: 50 dB or less (p6, 3-2-2).
- Connection: lead wire, Red (+), Blue (-) (p6, 3-1-2). The part is BLDC with a drive IC and Hall sensor (p8, circuit and part list).
- Life: 1,000,000 cycles, 2 s on and 1 s off, at DC 3.0 V (p11, 8-1).

### 1.5 Jinlong W0625SS001D (BLDC coin, Φ6 x 2.5 T) [F, third-party host]
- Source: Jinlong spec S-324456 (2018.07.17), hosted at https://file.aichiplink.com/r/datasheets/jinlongmachineryelectronicsinc-w0625ss001d-datasheets-0895.pdf (saved as `slim2_jinlong-w0625ss001d.pdf`, 11 pages). Third-party host, as above.
- Size: "Φ6 x 2.5T" (p2). Drawing (p11): ∅6 ±0.1; height 2.5 ±0.1; "Max 2.0" callout; poron sponge 1.0 mm thick (p11).
- Weight: about 0.90 g (p6, 8-3).
- Rated voltage: DC 3.0 V (p5, 7-1). Operating voltage range: DC 2.7 to 3.3 V (p4, 3-1).
- Rated load speed: 15,000 ±3,000 rpm (p5, 7-3). Rated load current: 90 mA max (p5, 7-4).
- Starting current: 175 mA max (p5, 7-5). Starting voltage: DC 2.5 V max (p5, 7-6).
- Vibration force: test item 8-1 on p6, value not in the extracted text.
- Connection: conflict. Section 7-2 says "Lead Wire Red to (+), Black or Blue to (-)" (p5). The drawing (p11) shows "Outter side (+) (Spring)" and "Outter side (-) (Spring)". Not resolved.
- Life: 1,000,000 cycles at DC 3.0 V, 0.5 s on, 0.5 s off (p7, 10-1 table).

### 1.6 Coin motors from round 1 (values copied from `slim.md` section 6, not re-read in this round)
- INEED C0620BLDCL27 (6 mm, BLDC): rated 3.0 V; rated current 80 mA max; starting current 150 mA max; starting voltage 2.5 V max; drawn body 2.0 ±0.1 + foam 0.3 + tape 0.15 (saved `slim_ineed-c0620bldcl27-spec.pdf`, p3, p4, p12).
- Vybronics VW0620AB001U (6 mm, BLDC): rated 3.0 V; rated current 80 mA max; starting current 150 mA max; starting voltage 2.5 V max; drawn body 2.0 ±0.1 + foam 0.3 (saved `slim_vybronics-vw0620ab001u.pdf`, p3, p10).

### 1.7 Checked and failed the size test
- PM 304-129.001 (Precision Microdrives, 4.4 mm diameter x 6 mm long, 2.7 V rated, 75 mA max current, 1.8 V max start; https://precisionmicrodrives.com/cdn/catalog_product/07103de6-bf39-4bf6-b02c-c49755fe3d6d/304-129.pdf, saved `slim2_pm-304-129.pdf`, p1, p3, p6). Fails: 4.4 mm is above 2.7 mm and the body is not the smallest dimension.
- PM 304-016.002 (4 mm diameter x 11 mm long, 1.5 V; saved `slim2_pm-304-016.pdf`, p1, p3). Fails.
- Vybronics VC0720B088L and the others above pass.

### 1.8 Not found
- Vybronics VZ4TL2B: the datasheet URL I tried (https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VZ4TL2B-datasheet.pdf) returned an HTML page, saved as `slim2_vybronics-vz4tl2b.pdf`. Not read.
- Vybronics VC0620B: no datasheet found (search "Vybronics VC0620B coin vibration motor datasheet pdf"; results gave VC0625B001L, VC0625B002L and VW0620AB001U only).
- Vybronics VZ43FC1B: search summary only [S]. The Vybronics spec is cited as rated 3.0 V, operating 2.5 to 3.4 V, rated speed 10000 +/-2500 rpm, rated current 100 mA max; the search summary gives a diameter of about 4.1 mm and a DigiKey footprint of 4.50 x 4.30 mm, which conflict. Not verified.
- Jinlong C0720 family: a 7 mm, 2.1 mm thick C0720B series is mentioned in search summaries [S] only (https://www.omo-ic.com/blog/2016-08/c0720b-series-coin-vibration-motors-319.html); the datasheet was not read.
- Jinlong W0520 and C0525: no datasheet found (search "Jinlong W0520 OR W0525 OR C0720 BLDC coin vibration motor specification pdf 2.5T"). A distributor lists an INEED C0525BLDCL27 (5 x 2.5 mm) [S] only.
- Jinlong C0620 (from the lead's list): no datasheet found; the search returned only the INEED C0620BLDCL27 listing.
- Precision Microdrives 304-100: no datasheet found in search.
- KOTL C0820B006F (LCSC copy): HTML, not read (`slim2_kotl-c0820b006f.pdf`).
- AAC and Jahwa parts, piezo benders at 3 V: not searched in this round (time).
- Coin motors of 6 mm at 2.0 mm height or less with a maker document: not found. The 2.0 mm bodies of the INEED and Vybronics VW0620 parts have foam and tape above or below (round 1).

## 2. Storage of 2 GB or more, smallest package, maker document

Result: no part in this list has a maker document that I could read with a package size under 6.2 x 8 mm. The CS CSNP32GCR01-BOW V1.0 maker document is read (8 x 6.2 x 0.75 mm, 8 pins). The CS CSNP16GCR01-AOW V1.1 maker document is read (16 Gbit = 2 GB, 8 x 6.2 x 0.75 mm). The MK-Founder and Zetta maker PDFs could not be downloaded (see below).

### 2.1 CS Semiconductor CSNP32GCR01-BOW, spec V1.0 (20 June 2022) [F]
- Source: saved `slim2_cs-sdnand-20230403.pdf` (11 pages). It was downloaded from https://atta.szlcsc.com/upload/public/pdf/source/20230403/5E099C1066F1A1514A630107F5026B52.pdf (distributor-hosted copy; the document names CS as the maker).
- Capacity: 32 Gb (p4, 1.1).
- Package: "LGA-8 package. The size is 8mm x 6.2mm x0.75mm." (p4, 1.1). Drawing table (p6): D 8.00 (7.90 / 8.10 min/max), E 6.20 (6.10 / 6.30), C 7.00 (6.90 / 7.10), pitch B 1.27 typ, H 0.80 (0.70 / 0.90), N 2.6 typ, M 3.5 typ. The table's symbol labels are not read as height; p6 header row is "Common Dimensions".
- Pads: 8, pin names: SDD2, CD/SDD3, SCLK, VSS, CMD, SDD0, SDD1, VCC in SD mode; RSV, CS, SCLK, VSS, DI, DO, RSV, VCC in SPI mode (p5, 2.1). SPI mode supported.
- Supply: Vcc 2.7 to 3.6 V (p4, 1.2).
- Standby current: less than 200 uA (p4, 1.2). Read, write and operating current: the performance page (p7) was not read.
- Operating temperature: 0 to +70 C (p4, 1.2). Storage: -25 to +85 C (p4, 1.2).
- Newer spec than V1.0.3: not established. The CS spec in round 1 (`slim_cs-sdnand-spec-sipeed.pdf`) is V1.0.3(2); I did not compare dates.

### 2.2 CS Semiconductor CSNP16GCR01-AOW, spec V1.1 (11 Oct 2023) [F]
- Source: saved `slim2_cs-csnp32gcr01-20240724.pdf` (19 pages, title "CSNP16GCR01-AOW", version V1.1, Oct 11, 2023). Downloaded from https://atta.szlcsc.com/upload/public/pdf/source/20240724/3566343115B6EEA16C90E32D746CA687.pdf. This is the 16 Gb sibling, not the 32 Gb part. Filename is misleading.
- Capacity: 16 Gb pSLC, which is 2 GB (p4, 1.1).
- Package: "LGA-8 package. The size is 8mm x 6.2mm x0.75mm." (p4, 1.1). Pads: 8 (p5, 2.1).
- SPI mode pins: CS, SCLK, DI, DO, VSS, VCC (p5, 2.1).
- Supply 2.7 to 3.6 V (p4, 1.2). Standby current less than 250 uA (p4, 1.2). Operating temperature -25 to +85 C (p4, 1.2).

### 2.3 Items I fetched that are not the parts asked for
- `slim2_cs-csnp32gcr01-20240730.pdf` is a Hanhai-tech SD NAND spec (HHW1GS60C / HHW2GS60C / HHW4GS60C, 128 MB to 512 MB, package 6.00 x 8.00 mm; p5 product list). Not CS, not 2 GB. Not used.
- `slim2_cs-csnp32gcr01-20260408.pdf` is an XTX Technology datasheet (XTSDx0xG, Rev 1.0, Mar 25 2026), not CS. Its scope: "1/2/4/8Gbit" (p1 title, p2 feature list), packages "8-pin WSON (8x6mm)" and "8-pin LGA(6x5mm) for 1.8V 1Gb/2Gb" (p2). So XTX has no 2 GB or larger part in this datasheet. Used only for the XTX row below.

### 2.4 MK-Founder MKDV32GCL-STH / -STP / -STL and MKDV16GCL-STP [S]
- Maker PDF not reached. The LCSC datasheet URLs https://datasheet.lcsc.com/lcsc/2212151403_MK-MKDV32GCL-STH_C5199868.pdf, https://datasheet.lcsc.com/lcsc/2402271621_MK-MKDV32GCL-STP_C7500179.pdf and https://www.lcsc.com/datasheet/lcsc_datasheet_2403241035_MK-MKDV16GCL-STP_C19192127.pdf returned HTML (`slim2_mk-mkdv32gcl-sth-lcsc.pdf`, `slim2_mk-mkdv32gcl-stp-lcsc.pdf`, `slim2_mk-mkdv16gcl-stp-lcsc.pdf`; 9 to 10 kB each). The wmsc URL for the MKDV16GCL-STP returned 143 bytes (`slim2_mk-mkdv16gcl-stp-wmsc.pdf`).
- A WebFetch of the Sekorm family copy (https://en.sekorm.com/doc/527569123.html) returned HTTP 457, no content.
- Listing sizes only [S]: MKDV32GCL-STH LGA-8 6 x 8 mm, 208 MHz (https://www.lcsc.com/product-detail/C5199868.html). MKDV32GCL-STP LGA-8 6.6 x 8 mm, 50 MHz (https://www.lcsc.com/product-detail/C7500179.html). MKDV16GCL-STP LGA-8 6.6 x 8 mm, 2.7 to 3.6 V, 50 MHz (search summary of https://lcsc.com/product-detail/NAND-FLASH_MK-MKDV16GCL-STP_C19192127.html). MKDV32GCL-STL: W-PDFN-8-EP 6 x 8 mm, 50 MHz SPI (https://jlcpcb.com/partdetail/MK-MKDV32GCLSTL/C2844071/C2844071) [S].
- Sekorm family copy, dated 2024-07-16, is said to show SPI support and a 3.3 V NAND supply (search summary [S]); the lines were not read by me, so this is not verified.

### 2.5 Zetta ZDSD32GLGEAG (LG package) and ZDSD32G/64G family
- Maker PDF for the LG part not reached. The LCSC datasheet URLs https://datasheet.lcsc.com/lcsc/2312110943_Zetta-ZDSD32GLGEAG_C5188571.pdf and https://lcsc.com/datasheet/lcsc_datasheet_2410010132_Zetta-ZDSD32GLGEAG_C5188571.pdf returned HTML (`slim2_zetta-zdsd32glgeag-lcsc.pdf`, `slim2_zetta-zdsd32glgeag-lcsc2.pdf`, 886 kB each, HTML).
- The saved Zetta family datasheet (`slim_szlcsc-0526-zetta-or-other.pdf`, 18 pages, round 1) has the package code "LV" only: "LV = LGA8x2 (Land Grid Array)" (`slim_zetta-p16-18.txt` line 56, p18 ordering key). "LG" does not appear in that document (search of `slim_zetta-p1-3.txt`, `slim_zetta-p4-5.txt`, `slim_zetta-p16-18.txt` for "LG" finds only "LGA" lines).
- LV package size: "LGA8x2 9x12.5mm" (`slim_zetta-p1-3.txt` lines 88 to 110; `slim_zetta-p16-18.txt` line 32, p17 section 9 "Package Dimensions"). Too large for the 6.2 x 8 mm limit.
- ZDSD32GLGEAG listing size: LGA-8 (6.2 x 8) (https://www.lcsc.com/product-detail/C5188571.html) [S].
- SPI mode and supply: family datasheet pin table (p4) lists SD and SPI modes; supply "2.7 to 3.6 V" for the 'SD' family and "Extended -25 to +85 C" (p18, ordering key). Currents not read.

### 2.6 Other storage parts
- XTX XTSD01G / 02G / 04G / 08G (1 to 8 Gb), maker document (round 1, `slim_xtx-xtsd0xglgeag-v2.pdf`), LGA8 8 x 6 mm. XTX XTSD16G: not found. The XTX 2026 datasheet (`slim2_cs-csnp32gcr01-20260408.pdf`, p1 title, p2 features) lists 1/2/4/8 Gb only. So XTX XTSD16G or larger: not in XTX's maker documents read.
- Longsys / FORESEE SD NAND 2 GB or larger: not found [S] (search "FORESEE OR Longsys SD NAND 32Gb LGA-8 6x8 datasheet pdf SPI mode"). Longsys results are SPI NAND (WSON-8 8 x 6 x 0.8 mm, 512 Mb to 4 Gb) and are not SD NAND [S].
- MK-Founder MKDV1GCL / MKDV2GCL / MKDV4GCL (1 to 4 Gb), round 1 maker document: under 2 GB, not counted.

### 2.7 Not found
- A 2 GB or larger part in a package under 6.2 x 8 mm, confirmed by a maker document I read: not found. The CS CSNP16GCR01-AOW and CSNP32GCR01-BOW are 8 x 6.2 mm, the same as the limit, not under it.
- MKDV16GCL-STP, MKDV32GCL-STH / -STP / -STL maker package drawing and pad count: not read (section 2.4).
- ZDSD32GLGEAG (LG) package size in a maker document: not read (section 2.5).
- CSNP32GCR01 read, write and standby currents, from the performance page: not read (p7 of the V1.0 spec).

## 3. Screen connector for Tailor Pixels TOH095XVT-01 tail

Result: the tail drawing gives the width, not the pitch. The 15-way connectors I searched for are not confirmed at the pitch the tail needs. Three matching connectors with a maker document are not found.

### 3.1 Tail geometry from the drawing [F]
- Source: `design/datasheets/display_TOH095XVT-01.pdf` page 5 (Tailor Pixels drawing TOH095XVT-01, rev V0), rendered and read.
- Visible callouts at the tail: "4.8" under the contact field (the contact span, 15 pins labelled 15 to 1); "0.2 ±0.03 incl. PI stiffener" on the stiffened end; "0.8 ±0.1" overall display thickness (page 5 drawing).
- Pitch: not labelled. Contact count is 15 (pin table p5: pins 1 to 15). If the 4.8 mm covers 15 contacts, the pitch is about 4.8 / 15 = 0.32 mm. A 0.5 mm pitch 15-way contact field is about 7 mm wide, which does not fit in 4.8 mm. So the pitch is at most about 0.3 mm. Inference, not a figure from the drawing.

### 3.2 Connectors searched [S]
- Molex 503480 (0.5 mm pitch): 12-way and 14-way listings (RS, DigiKey); 12-way right-angle height 1.00 mm (RS listing summary). No 15-way at 503480 found. Molex 503480-1510 part number: not found.
- Molex 502244 (0.5 mm pitch, 15-way, bottom contact, SMT right angle): 5022441530 height 2.33 mm (DigiKey listing summary, https://www.digikey.de/en/products/detail/molex/5022441530/2818926). Pitch 0.5 mm, so it does not fit the 4.8 mm tail; not a match.
- Molex FlexiSnap 15-way: height 1.5 mm and FFC thickness 0.30 mm (summary only, not confirmed as a 15-position part number).
- Molex 5007971594 (15-way, 0.30 mm pitch, bottom contact, SMT right angle; https://www.digikey.de/en/products/detail/molex/5007971594/1989267): listing summary only. Pitch 0.30 mm (in the listing name). Height, footprint and maker PDF not read.
- Hirose FH35C, FH26W, FH58; Kyocera 6843; Panasonic Y3B: not searched in this round (time).

### 3.3 Not found
- Three 15-position flat-cable connectors with a maker document (exact part, pitch, height, footprint depth and width, contact side, land pattern page): not found. Only the Molex 5007971594 listing [S] is at a pitch the tail may fit.

## 4. Cell: thin LiPo, 2.5 to 3.0 mm thick, 10 to 12 mm wide, 18 to 25 mm long

Result: no cell with a per-model page or datasheet in this round fits the size window. The Grepow search returned no model in the window. Other makers in the list (PATL, DTP, LiPol LP251020 / LP301020 / LP251218, Renata ICP) were not searched in this round (time).

### 4.1 Grepow
- Search "Grepow ultra-thin lithium polymer battery 2.8mm thickness 12mm width datasheet capacity 4.2V" [S]: the Grepow ultra-thin page states thickness "as thin as 0.5 mm to 1.5mm" (https://www.grepow.com/shaped-battery/ultra-thin-battery.html; search summary). Ultra-narrow page: width "4.1 mm", models with 2.16 mm and 2.38 mm thickness at 4.35 V (https://www.grepow.com/shaped-battery/ultra-narrow-battery.html; search summary). No model at 2.5 to 3.0 mm thick and 10 to 12 mm wide was in these summaries.
- Round 1 (`slim.md` section 2.1): the Grepow ultra-narrow table has GRP2409017 (2.22 x 9.6 x 17.55 mm, 24 mAh, 4.35 V), GRP2310021 (2.18 x 10 x 21 mm, 30 mAh, 4.35 V). Neither is in the full window (GRP2409017 width 9.6; GRP2310021 length 21). These are the round-1 WebFetch summary, not read as a saved copy.
- Grepow example from this search [S]: "55mmx22mmx0.4mm, 22 mAh" (ultra-thin listing, GRP0422055). Out of window.

### 4.2 Not found
- Cell at 2.5 to 3.0 mm thick, 10 to 12 mm wide, 18 to 25 mm long, with a per-model datasheet: not found in: grepow.com (ultra-thin and ultra-narrow pages, search summaries), grepow.com battery-news pages (search summaries). Not searched: PATL, Shenzhen Data Power DTP, LiPol LP251020 / LP301020 / LP251218, Renata ICP.
- Charge current, protection board and full-charge voltage per model: not read (no model in the window).

## Limits and what is not done
- Time: about 40 minutes used. Done: section 1 in full (five parts with maker documents), section 2 partly, section 3 partly (drawing read, no connector confirmed), section 4 partly (Grepow only).
- Not done: section 2 MK and Zetta maker documents (blocked: LCSC PDF URLs return HTML, mkfounder not found, Sekorm WebFetch HTTP 457); section 3 connector confirmations; section 4 PATL, DTP, LiPol, Renata.
- Two URLs I guessed for Vybronics (VC0625B001L, VC0625B002L, VC0720B088L) returned PDFs; they are the maker's own host. The Jinlong W0525AB001D and W0625SS001D specs come from a third-party host (file.aichiplink.com).

## questions_for_owner
- Is a third-party host acceptable for the Jinlong specs (section 1.4, 1.5), or should the lead get the originals from Jinlong directly? No purchase or contact was made.
- For section 2: is a 2 GB part at 8 x 6.2 mm (CSNP16GCR01-AOW, CSNP32GCR01-BOW) acceptable against the "smaller than 6.2 x 8 mm" limit? They match the limit, not beat it.

RESULT: done, section 1 has five vibration parts with maker documents (Vybronics VC0625B001L, VC0625B002L, VC0720B088L; Jinlong W0525AB001D, W0625SS001D), sections 2 to 4 are partly done with the blocked items listed under Not done.
