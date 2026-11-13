"""C5e (review 3, H03 and H16): P1-P4 in case-bom.csv is the Harwin P70-6000045R (the pin holder has four 1.60 mm bores for 1.50 mm barrels);
the Mill-Max 0981 stays only as a history line (quantity 0, reference PA1-PA4, kept so the designator set does not change); MECH1 outer size is 45.4 mm.
Run once: python3 look/c5e_bom.py (it edits rows by reference, a re-run changes nothing more)."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
BOM = os.path.join(os.path.dirname(HERE), "case-bom.csv")
rows = list(csv.reader(open(BOM, newline="")))
head = rows[0]
col = {k: i for i, k in enumerate(head)}
for r in rows[1:]:
    ref = r[col["reference"]]
    if ref == "P1-P4":
        r[col["function"]] = "spring pins VBUS D- D+ GND to the ring pads (fitted pin: Harwin P70-6000045R, 1.50 mm barrel, fits the pin holder's four 1.60 mm bores)"
        r[col["maker"]] = "Harwin"
        r[col["maker_part_number"]] = "P70-6000045R"
        r[col["package"]] = "SMT with peg"
        r[col["size_mm"]] = "barrel 1.50 x 1.85 (length is my reading)"
        r[col["key_figures"]] = "2.80 free height; 0.39 N +-0.09 N at 2.10 mm working height; 1 A; plunger 0.60; stroke NOT confirmed (not in the files read)"
        r[col["evidence"]] = "LIST"
        r[col["source_file_or_url"]] = "design/datasheets/p3_harwin_p70.txt; design/datasheets/p3_harwin_p70_chipdip.pdf; design/parts/ui-pass3.md line 190"
        r[col["open_action"]] = "[LIST] proposed, stroke not confirmed (conflict K1): confirm with Harwin the stroke, the force curve at 2.10 to 2.65 mm and the life; the pin must give at least 0.34 mm of stroke (out/case_params.json pin_travel needed_stroke 0.338, free height 2.80 to heights 2.280 to 2.418 mm)"
    elif ref == "PA1-PA4":
        r[col["quantity"]] = "0"
        r[col["function"]] = "history only, NOT fitted: Mill-Max 0981 spring pin, the first P1-P4 (C2); it does not fit: flange 2.11 mm against a 1.60 mm pad pitch, and the pin holder bores are 1.60 mm for 1.50 mm barrels"
        r[col["maker"]] = "Mill-Max"
        r[col["maker_part_number"]] = "0981-0-15-20-87-14-11-0"
        r[col["package"]] = "SMT spring-loaded pin"
        r[col["size_mm"]] = "flange 2.11 dia x 5.182 high"
        r[col["key_figures"]] = "stroke 1.397 mm; mid stroke 0.70 mm; 90 gf; 20 mOhm max; 100,000 cycles"
        r[col["evidence"]] = "DS"
        r[col["source_file_or_url"]] = "design/datasheets/p3_millmax_0981.pdf p.1 p.3"
        r[col["open_action"]] = "none: not fitted; the fitted pin is item 15 (P1-P4, Harwin P70-6000045R)"
    elif ref == "MECH1":
        r[col["function"]] = r[col["function"]].replace("45.5 x 45.9 x 41.4 mm", "45.4 x 45.9 x 41.4 mm")
with open(BOM, "w", newline="") as f:
    csv.writer(f).writerows(rows)
print("rows", len(rows) - 1)
