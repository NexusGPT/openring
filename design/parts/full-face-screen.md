# Full-face small AMOLED candidates

Question: which small AMOLED (or other self-lit) modules have a lit area close to 27.9 x 13.4 mm, and what are their real figures?

Target (for judgement only, not sent anywhere): face 29.1 x 14.56 mm, corner radius 2.5 mm, module must fit inside 29.1 x 14.56 mm (walls about 0.45 mm per side), thinner than the present 0.8 mm panel, SPI / QSPI / MIPI DSI with few pins, narrow flex.

Method: public product pages and PDF datasheets were downloaded with curl and read from saved copies in `<scratch>/full-face-screen-evidence/`. Figures from search snippets only are marked [S]. Figures read on a page or PDF are marked [F].

## Saved sources (URL → saved copy)

- S1: https://tailorpixels.com/wp-content/uploads/2025/04/TOH095XVT-01_0.95-inch-Small-AMOLED-Display-Bar-Type-120x240-SPI.pdf → `src2-16a2a210.bin.txt` (datasheet TOH095XVT-01, the present part family)
- S2: https://www.panoxdisplay.com/uploadfile/datasheet/BO095F120S.pdf → `src2-dc8aac5c.bin.txt` (datasheet BO095F120S)
- S3: https://www.panoxdisplay.com/amoled/0-95-amoled-120x240-spi.html → `src2-a8740229.bin` (listing copy, `pan095.txt`)
- S4: https://cdn.shopify.com/s/files/1/0829/9960/7616/files/1.4_INCH_AMOLED_DISPLAY_MODULE.pdf → `src3-8042654b.bin.txt` (Brownopto 1.4-inch spec, V0, released 2024.11.20)
- S5: https://panoxdisplay.com/application/oled-wearable-device.html → `src-acd0bd77.bin` (overview of wearable AMOLEDs, text `ali.txt`)
- S6: https://www.panoxdisplay.com/amoled/1-91-amoled-display-240x536.html → `src2-c8ca9042.bin` (listing copy, `pan191.txt`)
- S7: https://www.directindustry.com/prod/shenzhen-yousee-technology-co-ltd/product-4621447-2851391.html → HTTP 403 to curl (blocked, see `src-b2bb71a9.bin`); figures are from the search snippet only [S]
- S8: https://toppop.en.alibaba.com/product/1600218615360-817999646/... → served an anti-bot challenge page (`src-dfa8607e.bin`, `toppop.txt`); figures from the search snippet only [S]
- S9: https://gesight.com/product/1-47-inch-amoled-touch-display-194x368 → HTTP 500 to curl (`src-c870ef39.bin`, a 2482-byte error page); figures from search snippets only [S]
- S10: https://www.panoxdisplay.com/amoled/1-47-amoled-194x368-spi.html → fetched (`src3-a861b7b1.bin`), but the spec table values did not come through in the saved copy; not used for figures.

## Candidates

Each row: figures as read. "not stated" means no such figure on the cited source.

### 1. Tailor Pixels TOH095XVT-01 (the present part family, 0.95 inch)
- Source: S1, `src2-16a2a210.bin.txt`
- Diagonal 0.95 in [F] line 99 (table row "Display Size(Diagonal)")
- Pixels 120RGB x 240 [F] line 102
- Lit (active) area 10.8 (H) x 21.6 (V) mm [F] line 103
- Module outline 12.8 (H) x 27.35 (V) x 0.8 (T) mm [F] line 104
- Corner shape: not stated (rectangle dimensions only)
- Interface 4SPI [F] line 106
- Driver IC SH8501A [F] line 107
- Brightness 450 cd/m2 [F] line 111
- Pin count: not stated in the table lines read
- Cable width / exit side: not stated (the drawing shows an FPC tail; no width given in table)
- In production: not stated
- Fits 29.1 x 14.56: yes (27.35 x 12.8). Unlit border: 2.8 mm total at the ends (about 1.4 mm each end), about 1.0 mm each side.

### 2. BOE-made 0.95 inch, Panox listing BO095F120S (same 120x240 panel)
- Source: S2, `src2-dc8aac5c.bin.txt`; listing S3, `pan095.txt`
- Lit area 10.8 (H) x 21.6 (V) mm [F] PDF line 152
- Module outline 12.8 (H) x 27.35 (V) x 0.75 (T) mm [F] PDF line 145
- Interface 4-SPI [F] PDF line 155; driver IC RM69310 [F] PDF line 123
- Pin/FPC: "Excluding hooks, posts, FPC/FPC tail" note at PDF line 165; pin count not stated
- Brightness 300 cd/m2 typ [F] listing line 435 (the PDF gives a different luminance figure, not read)
- CONFLICT: the same listing (S3) gives "Bezel Area 32.1 (H) x 44.6 (V) x 0.75 (T) mm" and "Outline 32.1 x 44.6 mm" at lines 433 and 459. The PDF (S2) gives 12.8 x 27.35. The PDF value is used here; the listing value is treated as wrong.
- In production: not stated
- Fits: yes (27.35 x 12.8). Same unlit border as candidate 1.

### 3. Shenzhen Brownopto 1.4 inch, 128 x 400 (strip)
- Source: S4, `src3-8042654b.bin.txt`
- Diagonal 1.4 inch [F] line 87 (row "Display Size(Diagonal) 1.4")
- Pixels 128 x 400 [F] line 89
- Lit area 10.6752 (H) x 33.36 (V) mm [F] line 92
- Module outline 12.435 (H) x 38.410 (V) x 0.78 (T) mm [F] line 91
- Interface QSPI/SPI/Dual SPI [F] line 95; driver ICNA3306 [F] line 96
- Pin list runs to pin 30 (CTP pins 27-30 at lines 197-203) [F]
- Luminance Bp 550 / 600 nit [F] line 372 (column meaning not confirmed)
- Corner shape: not stated
- Cable width / exit side: not stated
- In production: not stated (V0 approval specification)
- Fits 29.1 x 14.56: NO (38.41 mm long, 12.4 mm wide). Lit length 33.4 mm is longer than the face.

### 4. EDO-made 1.47 inch 194 x 368 (Panox overview and third-party snippets)
- Overview: S5 `ali.txt` lines 378-385: "1.47 inch AM-OLED, 194x368 / Round Angle edge / Dot Matrix 194x368 / Interface Q-SPI / Driver IC SH8501B (COF) / Luminance 500 cd/m2" [F]
- Lit area 17.46 (W) x 33.12 (H) mm [S] (Slideshare / Panox snippet, query "EDO 1.47 inch AM-OLED 194X368 SPI datasheet outline dimension")
- Outline 19.36 x 36.17 mm [S] (gesight snippet, labels inconsistent in the snippet)
- Thickness, pin count, cable: not stated
- Part number E1473AC63 [S] (Slideshare snippet)
- In production: not stated
- Fits 29.1 x 14.56: NO (about 36 mm long, 19.4 mm wide outline). Its lit width (17.46 mm) is also above the 13.4 mm target width.

### 5. Shenzhen Yousee YX011T90332, 1.1 inch LTPS AMOLED, 126 x 294 (strip)
- Source: S7 (blocked to curl). Figures from search snippet [S] only.
- Pixels 126 x 294 RGB [S]
- Lit area 10.962 x 25.578 mm [S]
- Outline 12.96 x 30.94 mm [S]
- Driver JD9613, 3-wire / 4-wire SPI [S]
- Thickness, cable, pin count, brightness: not stated
- In production: not stated
- Fits 29.1 x 14.56: NO for length (30.94 > 29.1). Width 12.96 is within 14.56.

### 6. Toppop listing, 1.1 inch 126 x 294 strip (same format, different seller)
- Source: S8 (anti-bot page, not readable). Figures from search snippet [S] only.
- Outline 12.96 x 30.94 x 0.5 mm [S]
- Driver RM69310 / TMA525B [S]
- Interface 30-pin board-to-board [S] (search snippet: "30Pin IPS SPI Strip AMOLED")
- Fits 29.1 x 14.56: NO for length (30.94 mm).

### 7. EDO/Panox 1.91 inch 240 x 536 (long strip, MIPI)
- Source: S6 `pan191.txt`
- Pixels 240 (RGB) x 536 [F] line 415
- Lit area 22.40 (W) x 51.42 (H) mm [F] (label at line 420)
- Outline listed as 22.40 (W) x 51.42 (H) x 0.3 (T) mm [F] line 448 region (the outline equals the lit area, which is suspicious for a module listing; not verified)
- Driver RM67162 [F] line 417; signal MIPI 1-lane [F] line 435
- Luminance 350 cd/m2 typ [F] line 424 region
- Fits 29.1 x 14.56: NO (51.4 mm long).

### 8. Panox overview, 1.6 inch 320 x 360 (RM69090, SPI/MIPI) and 1.41 inch 320 x 360 (RM67162, MIPI 30 pins)
- Source: S5 `ali.txt` lines 344-356 (1.41: "Dot Matrix 320x360 / Driver IC RM67162 / Interface MIPI 30 pins" [F]); lines 389-396 (1.6: "Round Angle edge / Driver IC RM69090 / Luminance 500 cd/m2" [F])
- Lit area, outline, thickness: not stated on the overview page
- Fits: not assessed. Lit size and outline are not stated, and the 320 x 360 format is close to square, not the 2:1 strip the target needs. Not a candidate for the target.

### 9. Panox overview, 1.45 inch 280 x 280 (MIPI 20 pins, thinnest 0.7 mm)
- Source: S5 `ali.txt` lines 362-370 [F]: "the thinnest thickness of 0.7 mm / Interface MIPI 20 pins / Dot Matrix 280x280"
- Lit area, outline: not stated
- Not a candidate: square format.

## Judgement (my reading of the facts above, not part of the sourced figures)

1. No stock part reaches the target lit area of 27.9 x 13.4 mm. The only stock parts that fit inside 29.1 x 14.56 mm are 0.95 inch 120 x 240 modules (candidates 1 and 2). Their lit area is 21.6 x 10.8 mm.
2. The 1.1 inch 126 x 294 strip (candidates 5 and 6) has the closest lit length (25.6 mm), but its outline is 30.94 mm long, which does not fit a 29.1 mm face. Its lit length is 2.3 mm short of the 27.9 mm target.
3. Using the stock figures, the end border (outline minus lit length, divided by 2) is about 1.4 mm for candidate 1 and about 2.5 to 2.7 mm for candidates 3 and 5 (outline length minus lit length, total for both ends: 38.41 - 33.36 = 5.05 mm for 3; 30.94 - 25.58 = 5.36 mm for 5). The target needs about 0.15 mm per end inside a 28.2 mm outline (0.6 mm per end if the full 29.1 mm face is used), which no candidate here reaches.
4. Conclusion: no stock part gets the lit area within 1 mm of the face edge all round. The face needs a custom panel. A custom request should specify:
   - Lit (active) area: 27.9 x 13.4 mm, with the corner radius of the lit area if rounded.
   - Module outline: no more than about 28.2 x 13.7 mm (face minus walls), or 29.1 x 14.56 mm absolute maximum.
   - Thickness: 0.8 mm or less, with the stiffener behind the panel stated.
   - Drive area: folded behind the panel (COP / chip-on-plastic), so the unlit end is removed. Ask the maker to confirm the folded layout.
   - Interface: 4-SPI or QSPI, with pin count stated, and a flex cable width and exit side (end or side).
   - Driver IC and driver-board location, so the flex can be routed.
   - Brightness at least 450 cd/m2 typ, to match the present panel's stated figure (candidate 1, line 111).

## Could not verify

- Yousee YX011T90332 datasheet and thickness: the DirectIndustry page is blocked (HTTP 403), so every Yousee figure is from search snippets [S].
- Toppop 1.1 inch listing: the anti-bot page blocked reading. Its 0.5 mm thickness and outline are [S] only.
- Gesight 1.47 inch 194 x 368 page: HTTP 500, so the outline 19.36 x 36.17 mm is [S] only and its labels are inconsistent in the snippet.
- EDO / Panox E1473AC63 datasheet and drawing: not found. A Panox PDF URL I guessed returned 404 (`src3-08537a77.bin`, 146 bytes).
- Stock availability ("in production") for every candidate: not stated on any page read.
- Corner shape of the lit area for candidates 1-4: not stated on the pages read, except the overview's "Round Angle edge" (candidate 4, S5 line 379), which does not say whether it refers to the lit area or the outline.
- A broader vendor sweep (BOE, Visionox, RiTdisplay, Raystar, Winstar, Tianma, DWO, Shenzhen module houses) was not run beyond the searches listed. No 180 x 360, 172 x 640, or 1.2 inch elongated 2:1 AMOLED module was found in the searches.
- Searches run (standard mode): "1.0 inch AMOLED module 126x294 datasheet active area mm"; "small AMOLED display 194x368 smartwatch module active area outline thickness"; "full screen narrow bezel 1.0 inch AMOLED elongated 180x360 fitness band module"; "1.2 inch AMOLED 240x536 module datasheet active area outline"; "1.1 inch AMOLED 126x294 SPI module datasheet active area mm thickness"; "EDO 1.47 inch AM-OLED 194X368 SPI datasheet outline dimension"; "0.95 inch AMOLED 120x240 module Tailor Pixels datasheet active area"; "bar type AMOLED display module 1.2 inch elongated strip SPI datasheet active area thickness 0.8mm"; "ultra narrow bezel AMOLED strip display 1.1 inch 1.2 inch 180x360 OR 172x640 OR 240x536 module specification"; "Visionox flexible AMOLED 1.1 inch wearable datasheet active area chip on plastic bottom bonding"; "AMOLED 1.2 inch 180x360 display module smart band datasheet"; "Brownopto 1.4 inch bar type AMOLED 128x400 module outline 12.435 datasheet"; "Shenzhen Yousee YX011T90332 1.1 inch AMOLED datasheet JD9613"; "126x294 AMOLED module 1.1 inch datasheet RM69310 TMA525B outline active area"; "Panox 1.47 inch AMOLED 194x368 SPI datasheet active area 17.46 outline".
- Flexible / chip-on-plastic (folded drive area) parts in the 1.0 to 1.2 inch range: none found. The Visionox 1.2 inch G1120TB103GF is round (33.22 mm outline, [S]) and not checked further.

RESULT: done, 9 candidates reviewed (6 with figures read from a page or PDF, 3 from snippets); none reaches the 27.9 x 13.4 mm lit area within the 29.1 x 14.56 mm face, so a custom folded-drive panel request is needed.
