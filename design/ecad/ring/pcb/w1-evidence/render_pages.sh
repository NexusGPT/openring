#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# Renders the maker pages the footprints were read from (drawings have no text layer for their dimensions) into pages/, 100 dpi.
DS=$REPO_ROOT/design/datasheets
O=$REPO_ROOT/design/ecad/ring/pcb/w1-evidence/pages
mkdir -p "$O"
r() { pdftoppm -r 100 -f "$2" -l "$2" -png "$DS/$1" "$O/$3" 2>&1; }
r w1_hirose_fh35c_series_catalog.pdf 3 hirose_catalog_p3
r w1_hirose_fh35c_series_catalog.pdf 4 hirose_catalog_p4
r w1_hirose_fh35c-15s-0.3shw50_drawing.pdf 1 hirose_drawing_p1
r p3_sgm38046.pdf 18 sgm38046_p18
r slim2_cs-sdnand-20230403.pdf 5 cs_bow_p5
r slim2_cs-sdnand-20230403.pdf 6 cs_bow_p6
r w1_ti_sn74axc4t774.pdf 41 ti_axc4t774_p41
r motor_tlv755p.pdf 42 ti_tlv755p_p42
r codes_tpd4e05u06.pdf 29 ti_tpd4e05u06_p29
r antenna_johanson_2450AT18D0100001E.pdf 2 johanson_p2
r antenna_johanson_2450AT18D0100001E.pdf 3 johanson_p3
r w1_kyocera_cx2016db_catalog_page10.pdf 1 kyocera_cx2016db_p1
r w1_alps_skta_catalog.pdf 2 alps_skta_p2
r display_TOH095XVT-01.pdf 5 tailor_p5
r slim2_jinlong-w0525ab001d.pdf 9 jinlong_p9
r npm1304_datasheet_v1_0.pdf 152 npm1304_p152
r npm1304_datasheet_v1_0.pdf 155 npm1304_p155
r ../mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf 7 knowles_p7
r nrf54lm20x_caaa_ref_pcb_0_2.pdf 1 nordic_caaa_layout_p1
ls -la "$O" | awk '{print $5, $9}'
