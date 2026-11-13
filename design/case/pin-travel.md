# Harwin P70-6000045R: travel, working height, force, current, resistance, life

Question: what does the maker (Harwin) state for the pogo pin P70-6000045R (2.8 mm free height, SMT with peg)?
Checked on 2026-11-13 (clock from `date`: 07:13 CET). Project commit 01c4a350 (master).

## Already saved (project files, read first)

- `design/datasheets/p3_harwin_p70_chipdip.pdf` (page 286 of a Harwin catalogue, a distributor copy). It states: free height 2.8 mm (drawing); "0.39N ±0.09N at 2.10mm working height"; current "1A"; reel 1,800. It does NOT state a travel, a rated life, or a contact resistance. Its text copy is `design/datasheets/p3_harwin_p70.txt` lines 15 to 18, 41, 47.
- So the saved page alone cannot answer the travel, life or resistance question. The maker's own documents below do.

## Values (maker documents, saved)

| # | Value | Exact quote | Document (saved copy) | Page / line |
|---|---|---|---|---|
| 1 | Travel from free height | Not stated by the maker as a number. The drawing gives the lowest working height as a height dimension, labelled "MINIMUM WORKING HEIGHT/MAX ALLOWED TRAVEL", value 1.90. Derived from quoted values: 2.80 − 1.90 = 0.90 mm max, 2.80 − 2.20 = 0.60 mm min. **Derived, not stated by the maker.** | Drawing P70-6000045R, "Customer Information Sheet", sheet 2 of 2 (`design/datasheets/w15_harwin_drawing_P70-600.pdf`, render `w15_harwin_drawing_P70-600_page-1.png`) | PDF page 1, lower-left view, dimension 1.90 under the label. Image only (no text layer): read from the render. |
| 2 | Recommended working height | "2.10mm working height" (spec table); drawing: "NORMAL WORKING HEIGHT" with dimension 2.10. Working-height range stated: minimum compression 2.20 mm, maximum compression 1.90 mm. | Component specification C05604 Issue 4, 28/10/2026 (`design/datasheets/w15_harwin_component_spec_C056.pdf`, text `w15_harwin_component_spec_C056.txt`), section 2.4; also drawing p.1 | C05604 PDF page 3, line 92: "P70-6000045R Surface Mount Yes 1A 30mΩ 2.80mm 2.20mm 1.90mm 0.39 ±0.09 40 ±10 2.10mm". Drawing p.1 labels "MAXIMUM WORKING HEIGHT" 2.20, "NORMAL WORKING HEIGHT" 2.10, "MINIMUM WORKING HEIGHT/MAX ALLOWED TRAVEL" 1.90. |
| 3 | Spring force at that height | "0.39 ±0.09" N at 2.10mm (spec); drawing: "FORCE AT NORMAL HEIGHT = 0.39N ±0.09N". Forces at other heights: not stated. | C05604 (above); drawing p.1 SPECIFICATION block | C05604 PDF page 3, line 92 (column "Spring Force (N)" = 0.39 ±0.09, "Height at which force applies" = 2.10mm). Drawing p.1, lower-right SPECIFICATION block. |
| 4 | Current rating | "1A" (table, max); drawing: "CURRENT RATING = 1.0A" | C05604 (above); drawing p.1; product page | C05604 PDF page 3, line 92 ("Current Rating (max)" = 1A). Product page text `w15_harwin_product_P70-6000045R.txt` line 324: "1A". |
| 5 | Contact resistance | "30mΩ" (table, max); drawing: "CONTACT RESISTANCE = 30mΩ MAX" | C05604 (above); drawing p.1 | C05604 PDF page 3, line 92 ("Contact Resistance (max)" = 30mΩ). Drawing p.1 ELECTRICAL block. |
| 6 | Rated life in cycles | "10,000 mating cycles min" (series text, section 2.3); drawing for this part: "DURABILITY = 10,000 CYCLES" | C05604 (above); drawing p.1 MECHANICAL block | C05604 PDF page 2, line 50 ("Durability ... 10,000 mating cycles min"). Drawing p.1 MECHANICAL block. Not stated against a working height. |

Notes on the values:
- Value 1 is a derived figure only. The maker's own words are the label "MAX ALLOWED TRAVEL" next to the height 1.90; no travel number is written on the drawing or in the spec.
- Harwin's product page (`w15_harwin_product_P70-6000045R.txt` line 280) gives "2.8mm free height and 2.1mm working height", consistent with the above. It states no travel or life.
- Harwin's series datasheet PD012 (`w15_harwin_datasheet_PD012.pdf`, text `w15_harwin_datasheet_PD012.txt`, page 3, lines 52 to 53 "Durability: 10,000 mating cycles", lines 70 to 72 "Working height: 1.85mm to 9.25mm ... Contact resistance: 50mΩ max (Pogo Pins)") is a series document, not for this part. Its contact resistance (50 mΩ max) differs from the part's 30 mΩ in C05604 and the drawing; the part-level figure is used.

## Needed by the design

Line: needed by the design: travel of at least 0.34 mm, and force and life over a working height of 2.10 to 2.65 mm.

- Travel of at least 0.34 mm: **yes** against the quoted values. Derived from the maker's free height 2.80 mm and its minimum-compression working height 2.20 mm, the travel is 0.60 mm (the maker's max-allowed-travel dimension 1.90 gives 0.90 mm). The maker itself does not state a travel figure.
- Force and life over a working height of 2.10 to 2.65 mm: **cannot be said**. The maker states force only at 2.10 mm (0.39 ±0.09 N). The maker's working-height range ends at 2.20 mm (maximum compression), so the maker states nothing at 2.65 mm, and nothing between 2.20 and 2.65 mm. Life (10,000 mating cycles min) is stated without a working-height qualifier.

## Documents opened (every address)

Fetches (all by curl, saved under `design/datasheets/`, prefix `w15_harwin_`):
1. https://www.harwin.com/products/P70-6000045R, result HTTP 200. Saved `w15_harwin_product_P70-6000045R.html` and `.txt` (text extracted).
2. https://content.harwin.com/asset/7e9fa1a8-a9d7-4d62-ad13-0ebb46629d5c/DRG-02628-Technical-Drawing-Datasheet-P70-600-pdf.pdf, HTTP 200. Saved `w15_harwin_drawing_P70-600.pdf` (1 page, no text layer; render `w15_harwin_drawing_P70-600_page-1.png`).
3. https://content.harwin.com/asset/b89796d6-7f19-4a62-b14a-d218b6d40238/C056-C056XX-Component-Specification-Pogo-Pins-P70-Series.pdf, HTTP 200. Saved `w15_harwin_component_spec_C056.pdf` and `.txt` (3 pages).
4. https://content.harwin.com/asset/7a0954b3-a49f-4b55-a280-e7167761e8d5/CPPOGO-Pogo-Pins-graph-of-complete-range-of-heights-and-compression.pdf, HTTP 200. Saved `w15_harwin_graph_CPPOGO.pdf` and `.txt` (2 pages). Table of heights, force, current, durability for every part; consistent with C05604. P70-6000045R row: free 2.8, max working 2.2, normal 2.1, min working 1.9, 0.39N, 1A, 10,000 durability.
5. https://content.harwin.com/asset/e912e501-e840-4b79-b49b-06ec534dedd0/PD012-Product-Datasheet-POGOPINS-Pogo-Pins-and-Contact-Pads-EZi.pdf, HTTP 200. Saved `w15_harwin_datasheet_PD012.pdf` and `.txt` (7 pages). Series-level.

Searches (not fetches): two web searches for the order code and the Harwin series. Results included distributor pages (DigiKey, element14). Those pages were NOT opened, so no value is taken from them. Not fetched: the other download links on the product page (RoHS, REACH, material, CMRT, EMRT, POPs, training module, environmental statement); none states travel or life.

Not done: no sign-up, account, form, purchase or supplier contact. No request named the project, owner or any linked company. No existing file of the project was changed.

## Not found

- Travel (stroke) as a number: not stated by the maker in the product page, drawing, C05604, CPPOGO graph, or PD012. Searched by reading all text of the saved files and the drawing render for "travel" and "stroke". The drawing's "MAX ALLOWED TRAVEL" is a label only.
- Force at any height other than 2.10 mm: not stated for P70-6000045R in any saved document.
- Life at a working height: not stated; only the series-wide 10,000 mating cycles.

## Case files (not changed)

`design/case/case-architecture.md` lines 45, 108, 204 to 215 and 241 call the stroke, force curve and life "not in the files read" and assume a 2.15 to 2.65 mm window. This answer finds the maker's working range is 1.90 to 2.20 mm, which does not cover 2.20 to 2.65 mm. Those lines were not edited (owner decision).

## questions_for_owner

1. The maker's working range for this pin ends at 2.20 mm (min compression). Can the design's window of 2.15 to 2.65 mm (case-architecture line 204) be moved down to 1.90 to 2.20 mm, or does the design need a pin rated above 2.20 mm? If it needs 2.65 mm, the maker's data cannot support it.
2. Should a force and life test at 2.20 to 2.65 mm (bench or supplier request) be added to the list, since the maker states none?

RESULT: done, travel is "yes" against the maker's quoted heights (derived 0.60 to 0.90 mm, not stated), while force and life over 2.10 to 2.65 mm cannot be said because the maker's working range ends at 2.20 mm.
