# Custom and band parts: interfaces

Band parts (J_BAND_A, J_BAND_B, SW1 to SW5, M1, BT1 with PRT1, RT1, CP1 to CP4): see `design/ecad/band/band-interface.md`. Their footprints are in `design/ecad/band/OpenRingBand.pretty`.

## TP1 to TP22: test pads

Footprint `OpenRing:TESTPAD_0.8`. Bare copper round pad, 0.8 mm (the size of the first draft, kept: `parts.csv` footprint name TESTPAD_0.8). The count 22 is the list TPS in `ecad/ring/make_netlist.py`.
