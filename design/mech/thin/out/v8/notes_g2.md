The path of each board against the model is in g.3 (every board within 0.05 mm: `boards over 0.05 mm` line). check_band.py compares each flat outline with `model_lengths.csv` (v7 totals plus FOOT_EXTRA) and with band_geom.py's formulas; it does not read the new STEP files, so its pass does not by itself prove the new files; g.3 does that.

