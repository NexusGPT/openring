# Licences of OpenRing

Copyright 2026 the OpenRing authors.

OpenRing is released under three licences, chosen by what a file is. The full texts are in `LICENSES/`.

| What | Where | Licence | Text |
|---|---|---|---|
| Hardware design: the 3D models (STEP, GLB, STL), the wiring (KiCad schematics, symbols, netlists, the circuit board file), the parts lists (`bom.csv`, `case-bom.csv` and the other `.csv` parts lists), the manufacturing drawings (SVG, and the PDF drawings and schematics we made) | `design/` | CERN-OHL-S-2.0 (CERN Open Hardware Licence Version 2, Strongly Reciprocal) | `LICENSES/CERN-OHL-S-2.0.txt` |
| Software: the ring firmware, the explorer app, and every script (`.py`, `.sh`) in the repository, wherever it sits (this includes the scripts under `design/`) | `firmware/`, `explorer/`, `tools/`, and every `.py` and `.sh` file | Apache-2.0 | `LICENSES/Apache-2.0.txt` |
| Documents: every `.md` file, the PDF documents, the pictures (PNG, JPG) | everywhere (`requirements.md`, `design/*.md`, `firmware/docs/`, `explorer/docs/` and the rest) | CC-BY-4.0 (Creative Commons Attribution 4.0 International) | `LICENSES/CC-BY-4.0.txt` |

How to read the table:

- The folder decides first, the file type decides where a file would fit two rows. A script inside `design/` is Apache-2.0 (software); a `.md` file inside `design/` is CC-BY-4.0 (document); a 3D, wiring, parts-list or drawing file inside `design/` is CERN-OHL-S-2.0.
- Logs, check outputs and other generated text files are documents (CC-BY-4.0) unless they sit in a folder that is software (`firmware/`, `explorer/`), where they follow that folder (Apache-2.0).
- Our own files carry no licence header; this file and the folder rule are the licence statement. A file that came from somebody else keeps its own notice (see `NOTICE.md`).
- Third-party parts, tools and documents keep their own licences. They are named in `NOTICE.md`. The makers' datasheets are not included.
