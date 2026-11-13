# Notice

OpenRing: Copyright 2026 the OpenRing authors. Licences: see `LICENSE.md` and `LICENSES/`.

This file names what the project uses but does not contain, and what in it came from somebody else.

## Used, not contained (fetched or installed by the reader)

| What | Where it is used | Licence (as stated by its project; check the version you fetch) |
|---|---|---|
| nRF Connect SDK v3.4.2 (Nordic Semiconductor), fetched by `west` from `firmware/west.yml` | firmware build and tests | mostly Apache-2.0 with some parts under the Nordic 5-Clause licence; read the notices in the SDK |
| Zephyr RTOS (a part of the SDK, fetched by `west`) | firmware build and tests | Apache-2.0 |
| BabbleSim (simulated radio, fetched by `west`, `firmware/west.yml`) | simulated-chip tests | Apache-2.0 |
| Nordic's toolchain container image `ghcr.io/nrfconnect/sdk-nrf-toolchain:v3.4.2` | `firmware/tools/Dockerfile` | the licences of its parts |
| KiCad (`kicad-cli`) | the wiring checks run it to export netlists and to run the electrical rules check | GPL-3.0 (a tool, not distributed here) |
| build123d and OpenCASCADE | the scripts that build the 3D models | Apache-2.0 (build123d); LGPL-2.1 with exception (OpenCASCADE) |
| Python packages in the project's virtual environment (not included) | the check scripts under `design/` | their own licences |
| npm packages named in `explorer/package.json` (React, Vite, three.js, Playwright and others, fetched by `npm install`) | the explorer app | their own licences (mostly MIT) |
| Fonts Geist Sans, Geist Mono and Libre Caslon Text, from the npm packages `@fontsource/*` | the explorer app (not embedded in this repository) | SIL Open Font License 1.1 |

KiCad symbols: the schematic symbols and footprints are the project's own (library `ring` in `design/ecad/ring/ring.kicad_sym` and `design/ecad/case/case.kicad_sym`); no KiCad library symbol is embedded. Fonts: none are embedded in this repository.

## Maker datasheets are not included

Maker datasheets, application notes, web pages and their text extracts are not included. Each belongs to its maker. `design/datasheets/README.md` lists, for each bought part of the two parts lists, the maker, the maker part number and the title of the document the project cites.

## Files in this repository that came from, or quote, Nordic's SDK or Zephyr

Result of the search (see `firmware/` for the whole tree): no source, header, build or configuration file of `firmware/app`, `firmware/modules`, `firmware/tests` or `firmware/tools` is a copy of a Nordic or Zephyr sample or file. Their `#include` lines and `Kconfig` symbols use the SDK; the SDK is fetched by `west`. The stock samples are built from the fetched SDK, not copied:

- `firmware/tools/bsim_hr_demo.sh` builds and runs the Zephyr samples `peripheral_hr` and `central_hr` from the SDK tree (the run follows Zephyr's `nrf52_bsim` documentation); it holds none of their code.
- `firmware/tools/kit_samples.sh` builds Nordic's samples `peripheral_hids_keyboard` and `peripheral_ancs_client` from the SDK tree; it holds none of their code.
- `firmware/tests/bsim/probe-nrf54/stock_conn.sh` and `stock_conn_plain.sh` build and run Zephyr's own BabbleSim test `tests/bsim/bluetooth/ll/conn` unmodified from the SDK tree.

The following files are logs that print excerpts of SDK or Zephyr files while the builder explored the SDK. The excerpts keep their original notice lines (Copyright Nordic Semiconductor ASA, Copyright Oticon A/S, SPDX-License-Identifier lines) exactly as printed and stay under the licence those lines name; they are not covered by our licences:

- `firmware/build-logs/probe-nrf54/20261111-211453-find3.log`
- `firmware/build-logs/probe-nrf54/20261111-211516-find4.log`
- `firmware/build-logs/probe-nrf54/20261111-211540-find5.log`
- `firmware/build-logs/probe-nrf54/20261111-211608-find6.log`
- `firmware/build-logs/step2/20261111-125510-explore3.log`
- `firmware/build-logs/step2/20261111-130556-explore9.log`
- `firmware/build-logs/step2/20261111-133453-peek9.log`
- `firmware/build-logs/step2/console-peek9.txt`
- `firmware/build-logs/step2/console9.txt`

`design/software/research-production.md` quotes one licence identifier of Nordic's `nrfxlib` in a sentence; it contains no code.

Copies of Apple documentation pages and of Nordic kit files that were kept in `firmware/build-logs/step3/` (`apple/`, `kit/`) are not included.
