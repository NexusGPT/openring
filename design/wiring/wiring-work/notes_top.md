## How to rebuild (for the lead; run in this order from the project root)

1. `python design/wiring/build_wiring.py` (re-runs itself under KiCad's Python; reads the ring board and design/wiring/ring-case-contact.csv as they are; writes design/wiring/product-wiring.csv)
2. `python design/wiring/check_wiring.py` (consistency; must end RESULT PASS)
3. `python design/wiring/check_wiring.py --require-complete` (exit 0 only when every conductor is complete; prints `COMPLETE <n> of <total> conductors (<percent>)` and each incomplete line with what it waits for)
4. `design/.venv/bin/python design/wiring/wiring-work/make_broken.py` (7 broken copies; last line BROKEN COPIES PASS)
5. `design/.venv/bin/python design/wiring/draw_wiring.py` (product-wiring.svg and .pdf; prints both counts)

