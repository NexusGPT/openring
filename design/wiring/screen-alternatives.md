# Screen alternatives: stock 0.95 inch 120 x 240 AMOLED modules and their cables

Written 2026-11-13, clock read at 04:30 CET (`date`). Writer: the screen-alternatives helper (task of the lead). Web: 22 requests of 25 (WebSearch, WebFetch and curl only; no browser; no form, account or message to any maker or reseller). No design file was changed. No git command was run.

Question: which stock AMOLED (or other self-lit) modules have a glass that fits about 12.8 x 27.4 mm, and what does each maker's drawing say about its flat cable?

Room in the ring (lead's brief, `screen-cable-study.md` section 3): a pocket 5.4 mm wide at one end of the glass, a connector 3.5 mm of path away.

Document paths are in `ROOT/design/datasheets/`. "p." is the PDF page (checked with `pdftotext -f N -l N`). `[not sourced]` marks a value from a search snippet or a web summary, never used as a value.

## Result in one view

Two modules in the saved files print the cable outline on their drawing page (Tailor Pixels, BOE/Panox). Both cables fail the 5.4 mm pocket as they are. Truly TR095A120SPC has no drawing page in the saved copy, and no other reachable copy has one. BuyDisplay, Densitron and Gesight were blocked or gated, so their cables are "cable not drawn" in every copy I could open. No stock module with a cable narrower than 5.4 mm at the glass was found.

## Module Tailor Pixels TOH095XVT-01

Documents: `design/datasheets/display_TOH095XVT-01.pdf` (saved earlier) and `design/datasheets/w14_tailor_toh095xvt-01_2025.pdf` (fetched 2026-11-13 from `https://tailorpixels.com/wp-content/uploads/2025/04/TOH095XVT-01_0.95-inch-Small-AMOLED-Display-Bar-Type-120x240-SPI.pdf`). The two files are byte-identical (md5 b4318928c9a755f1ce4b6a73e6978261), so the saved copy is the maker's current upload.

1. Glass and module size, active area, pixels:
   - Module outline 12.8 (H) x 27.35 (V) x 0.8 (T) mm; p.4, module parameter table.
   - Active area 10.8 x 21.6 mm; p.4.
   - 120 x 240 RGB; p.4.
2. Cable:
   - Width at the glass: 12.4 mm. Not printed. Vector measurement by the study (`screen-cable-study.md` line 42: "12.401 wide"); my visual check of p.5 agrees that the wide part is near the glass width.
   - Widths along the cable: wide part 12.4 for about 12 mm, then a neck of 4.8 mm (printed "4.8", p.5; the study's line 43 gives the neck's start at 12.5 mm).
   - Length: 20 mm, printed "20" on p.5 (from the panel end to the cable end).
   - Contacts: 15, printed "15 ... 1" on p.5. Pitch: not printed; the study's 0.297 (`screen-cable-study.md` line 49) is a vector reading.
   - Thickness: 0.2 +-0.03 at the contact end including the PI stiffener, printed on p.5. Thickness elsewhere: not printed.
   - Contact field and stiffener: 3.2 mm long, printed "3.2" on p.5.
   - Driver chip place: not stated in the document. The notes on p.5 print "DRIVER IC: SH8501A" with no location.
3. Interface and supplies (p.6): 4-SPI (p.4). VCI 2.7 to 3.6 V; IOVCC 1.65 to 3.3 V; ELVDD 4.55 to 4.65 V; ELVSS -2.3 to -2.1 V. Touch: none; the TP rows read "/" (p.4).
4. Fits the 5.4 mm pocket as it is: **no.** The decisive number is the 12.4 mm wide part along the first 12 mm from the glass (vector, `screen-cable-study.md` line 42). The 4.8 mm neck is narrower, but it starts 12.5 mm from the glass, and the 12.4 mm part lies between.
5. Saved documents: `design/datasheets/display_TOH095XVT-01.pdf`; `design/datasheets/w14_tailor_toh095xvt-01_2025.pdf`.

## Module BOE (sold by Panox Display) BO095F120S

Documents: `design/datasheets/bench_panox-bo095f120s.pdf` (saved earlier; identical to `slim_panox-bo095f120s.pdf`) and `design/datasheets/w14_panox_bo095f120s.pdf` (fetched 2026-11-13 from `https://www.panoxdisplay.com/uploadfile/datasheet/BO095F120S.pdf`; md5 1292a0d0f53ce50811941eb5fdbf4e29, identical to the saved copies). Maker's panel name on p.5: "BOE0.95AMOLED". The listing page `https://www.panoxdisplay.com/amoled/0-95-amoled-120x240-spi.html` (curl, 200) lists only this part for 0.95 inch 120 x 240.

1. Glass and module size, active area, pixels:
   - Module outline 12.8 (H) x 27.35 (V) x 0.75 (T) mm; p.4. The drawing on p.5 prints 12.8 +-0.2 (panel) and 27.35 +-0.2 (panel), and 12.6 +-0.2 (POL).
   - Active area 10.8 x 21.6 mm; p.4.
   - 120 RGB x 240; p.4.
   - Corroboration, not a value: `https://marketplace.oled-info.com/view/174/BOE095-120240` (WebFetch summary, not saved) gives panel 12.8 x 27.35 and thickness 0.75 [not sourced].
2. Cable (drawing p.5, front, side and back views):
   - Width at the glass: not printed. Derived from two printed numbers: a dimension "7" spans the lower tail, and a dimension "5.6" spans the step from the wide cable to the tail. 7 + 5.6 = 12.6 mm [derived from printed numbers, not a printed width]. The visual check of p.5 agrees the cable runs at about the POL width (12.6) down to the bend.
   - Widths along it: wide part about 12.6 mm to the bend area (a hatched "bend area" on p.5); lower tail 7 mm (printed "7", p.5), where the connector sits.
   - Length: not printed. Estimated from the drawing's proportions at about 27 mm from the glass end to the connector [estimate from proportions, not a printed dimension].
   - Contacts: 20 (pin numbers 1 to 20 printed on the p.5 drawing). Pitch: not dimensioned. The connector code printed on p.5 begins "BM23F0.6-20DP"; the 0.6 is read from the code only [not dimensioned].
   - Thickness (all printed on p.5): FPC 0.13 mm; stiffener 0.15 mm + 0.3 mm at the connector; connector 0.51 mm; total with solder 1.265 mm. A label reads "钢片补强T=0.2mm" (stiffener T 0.2) on the side view at the cable's lower end.
   - Driver chip place: p.5 notes read "5. DRIVER IC: RM69310" and "6. CONNECTOR: COG+FPC". The term COG usually means chip on glass; read as chip on glass [reading of a printed term, not dimensioned].
   - Other printed notes on p.5: "元件区域, 限高0.8mm" (component area, height limit 0.8 mm) on the glass side of the cable.
3. Interface and supplies (p.8): 4-SPI (p.4); RM69310 (p.4). VDD 2.4 / 2.8 / 3.3 V; VCI 2.4 / 2.8 / 3.3 V; IOVDD 1.65 / 1.8 or 2.8 / 3.3 V; ELVDD 4.6 V; ELVSS -2.4 V (p.8, electrical specification). Touch: "TP Outline TBD" (p.4); pins 15 to 19 are "Touch reserved" (p.6). Touch: not present in the printed spec.
4. Fits the 5.4 mm pocket as it is: **no.** Decisive number: the cable is about 12.6 mm wide at the glass (derived). Even the 7 mm tail, printed on p.5, is wider than the 5.4 mm pocket, and the connector is at the far end of a long tail.
5. Saved documents: `design/datasheets/w14_panox_bo095f120s.pdf`; `design/datasheets/bench_panox-bo095f120s.pdf`.

## Module Truly TR095A120SPC (reseller copy by Panox Display)

Documents: `design/datasheets/display_TR095A120SPC.pdf` (saved earlier; identical to `slim_truly-tr095a120spc.pdf`) and `design/datasheets/w14_truly_tr095a120spc.pdf` (fetched 2026-11-13 from `https://www.panoxdisplay.com/uploadfile/datasheet/TR095A120SPC_1-10_1.pdf`; md5 1b65ba597c06d88f729b2ad6ed5b648f, identical). Maker is Truly (Huizhou); the file is dated Jan 18, 2019, version 0.1.

1. Glass and module size, active area, pixels:
   - LTPS glass outline 12.8 x 27.35 mm; encapsulation glass 12.8 x 24.4 mm; total thickness 0.78 mm; p.5 (general information). Active area 10.8 x 21.6 mm; p.5.
   - Pixel pitch 80 um; printed as "80× 80 um", p.5.
2. Cable: **cable not drawn.** The file has 10 pages. The contents list on p.3 names "EXTERNAL DIMENSIONS" (between "INTERFACE DESCRIPTION" and "PACKING SPECIFICATION"). The file goes from INTERFACE DESCRIPTION (p.8) straight to "Module Block Diagram" (p.9). **The missing page is the EXTERNAL DIMENSIONS page.** No cable width, length, pitch or thickness is printed anywhere in the saved copy.
   - Contacts: 30, printed on p.8 (pins 1 to 30; touch pins TP_SDA, TP_SCL, VDD_TP, TP_INT, TP_RST; NFC pins AN_A, AN_B).
3. Interface and supplies: SPI (p.4); RM69310 (p.4). VDDIO 1.65 / 1.8 / 3.3 V (p.5, electrical table). Other rails: not extracted in this pass. Touch: yes (30-pin list, p.8).
4. Fits the 5.4 mm pocket as it is: **cannot be told.** Decisive number: no cable dimension exists in any saved copy. The 30-contact cable is not the 15-contact cable of J1 (`screen-cable-study.md` section 7.3).
5. Saved documents: `design/datasheets/display_TR095A120SPC.pdf`; `design/datasheets/w14_truly_tr095a120spc.pdf`.

## Module BuyDisplay ER-OLED0.95-4C (SH8501, plug-in FPC)

Documents: none saved. Blocked.
- `https://www.buydisplay.com/0-95-inch-micro-full-color-amoled-display-panel-rgb-120x240-sh8501-spi` (WebFetch: HTTP 403; curl: Cloudflare "Just a moment..." challenge page).
- `https://www.buydisplay.com/chinese/0-95-inch-micro-full-color-amoled-display-panel-rgb-120x240-sh8501-spi` (curl: same challenge page).
- Search snippets (not sourced): outline 12.80 x 27.35 x 0.8 mm; a 15-pin 0.3 mm pitch ZIF connector drawing linked from the page; driver SH8501.

1. Glass and module size: 12.80 x 27.35 x 0.8 mm [not sourced, search snippet].
2. Cable: **cable not drawn** in any copy I could open. A "15-pin, 0.3 mm pitch ZIF connector drawing" is named in a snippet only [not sourced].
3. Interface: SPI (snippet) [not sourced]. Supplies, touch: not read.
4. Fits the 5.4 mm pocket: **cannot be told.** No cable drawing.
5. Saved documents: none.

## Module Densitron DMA010Q6NSNT0-1A

Documents: none saved. Gated.
- `https://www.densitron.com/displays-computers/0-95-amoled` (WebFetch, 1 request). Its product spec link `https://www.densitron.com/gated-file-form?file=270` is a gated form. I did not fill in or submit it.

1. Size: "Dimensions Width 12.80 mm", "Height 27.35 mm", "Depth 0.74 mm", "Interface SPI" [not sourced: WebFetch summary, no saved copy].
2. Cable: **cable not drawn** (the spec is gated; the page prints no drawing).
3. Driver, pins, supplies: not read.
4. Fits the 5.4 mm pocket: **cannot be told.**
5. Saved documents: none.

## Module Gesight TR095A120SPC (0.95 inch LTPS, reseller page)

Documents: none saved. Not readable.
- `https://gesight.com/product/0-95-inch-ltps-amoled-display-120x240-spi` (curl: "Database Error" page).
- `https://gesight.com/interface/spi` (curl: same "Database Error" page).
- Search snippet (not sourced): "30-pin FPC connection" and "built-in ZTW523 touch IC" for the TR095A120SPC module.

1. Size: not read.
2. Cable: **cable not drawn**; the page's "Display Drawing" link is not reachable.
3. Interface: SPI (page title); touch IC ZTW523 [not sourced].
4. Fits the 5.4 mm pocket: **cannot be told.**
5. Saved documents: none.

## Modules checked and not candidates (saved)

- DM-OLED095-626, Display Module (`design/datasheets/slim_dm-oled095-626.pdf`, p.3): 96 x 64 pixels, controller SSD1331, module 25.70 x 22.20 x 1.50 mm. Fails the glass and thickness limits.
- DM-OLED096-658, Display Module (`design/datasheets/slim_dm-oled096-658.pdf`, p.3): 64 x 128 pixels, controller SH1107, module 14 x 28 x 1.22 mm. Fails the glass and thickness limits.
- JX943 AMOLED (`design/datasheets/slim_szlcsc-0ee5.pdf`, p.4, "Dimension outline"): 43.20 x 43.20 x 2.55 mm, QSPI, ST7801N. Fails the size limit; not a candidate.
- Dfrobot ZXYQ667009 (copy in the scratchpad folder, not saved in datasheets; not cited as a value): 6.67 inch, 1080 x 2400, MIPI. Fails the size limit; not a candidate.

## Search and fetch log (22 web requests in all)

1. WebSearch "0.95 inch AMOLED 120x240 module datasheet mechanical drawing FPC": listing pages (BuyDisplay, Gesight, Panox, Tailor, BOE marketplace).
2. WebSearch "0.95" AMOLED 120x240 SH8501A module datasheet pdf": same set plus Densitron.
3. WebFetch Densitron product page: gated spec link only.
4. WebFetch BuyDisplay product page: HTTP 403.
5. curl Panox 0.95 list page: 200; only BO095F120S listed.
6. curl BuyDisplay product page: Cloudflare challenge.
7. curl Gesight product page: "Database Error".
8. curl Tailor 2025 PDF: 200; identical to saved copy.
9. curl Panox-hosted Truly PDF: 200; identical to saved copy.
10. WebSearch "0.96 inch AMOLED 120x240 display module SPI drawing pdf": no 0.96 inch 120 x 240 module found.
11. WebSearch Visionox / RiTdisplay / Truly: no RiTdisplay or Visionox datasheet in results.
12. WebSearch RM69310 120x240: Panox copy only.
13. WebSearch TR095A120SPC drawing: Panox-hosted Truly copy; no drawing found.
14. WebSearch RiTdisplay / Visionox / EDO / Tianma: no matching maker document.
15. curl texim-europe getfile id=102872: HTML error page, not a PDF; deleted.
16. curl DFRobot ZXYQ667009 PDF: 6.67 inch; not a candidate.
17. WebFetch OLED Marketplace BOE095-120240: panel 12.8 x 27.35, thickness 0.75, no drawing link.
18. WebSearch BOE BO095F120S drawing: Panox copy; no bend dimension in snippet.
19. curl BuyDisplay Chinese page: Cloudflare challenge.
20. curl Gesight SPI page: "Database Error".
21. WebSearch Newhaven / Winstar / Raystar 120x240 AMOLED: none; Newhaven 0.95 inch is 96 x 64; Raystar parts are 0.96 inch monochrome [search snippet, not sourced].
22. curl Panox BO095F120S PDF: 200; identical to saved copies.

Not found: a 0.96 inch AMOLED 120 x 240 module (search 10); a RiTdisplay, Visionox, EDO or Tianma 0.95 inch 120 x 240 module (search 11, 14); a Newhaven, Winstar or Raystar 120 x 240 AMOLED (search 21). Searched: the search terms above, in the results of those 21 searches. Not searched: the makers' own websites (no address was given for them in the brief except the reseller pages above).

## Table: module, glass, cable width at the glass, fits as it is

| Module | Glass (mm) | Cable width at the glass | Fits as it is |
|---|---|---|---|
| Tailor Pixels TOH095XVT-01 | 12.8 x 27.35 (p.4, p.5) | 12.4, vector, not printed (study line 42) | no |
| BOE / Panox BO095F120S | 12.8 x 27.35 (p.4) | about 12.6, derived from printed 7 + 5.6 (p.5) | no |
| Truly TR095A120SPC | 12.8 x 27.35 (p.5) | not drawn; EXTERNAL DIMENSIONS page missing | cannot be told |
| BuyDisplay ER-OLED0.95-4C | 12.80 x 27.35 [not sourced] | not drawn; site blocked | cannot be told |
| Densitron DMA010Q6NSNT0-1A | 12.80 x 27.35 [not sourced] | not drawn; spec gated | cannot be told |
| Gesight TR095A120SPC | not read | not drawn; page error | cannot be told |

## questions_for_owner

- Truly EXTERNAL DIMENSIONS page: it is not in the saved copy. A request to Truly (or a distributor) is needed to read the cable. I did not contact any maker; the lead decides.

RESULT: done, two stock 0.95 inch 120 x 240 modules (Tailor TOH095XVT-01 and BOE/Panox BO095F120S) have maker drawings and both cables fail the 5.4 mm pocket as they are; Truly, BuyDisplay, Densitron and Gesight have no readable cable drawing, and no stock module with a cable narrower than 5.4 mm at the glass was found.
