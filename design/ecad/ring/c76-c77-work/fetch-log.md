# Fetch log, C76 and C77 part search (2026-11-13)

Client identity sent: generic `Mozilla/5.0 (generic client)`. No name, company, e-mail or project name in any request. No sign-up, login, form or supplier contact. Times are from `date` (Europe/Paris, CET) in the same command as each fetch, unless marked "not captured".

## Direct fetches (curl, raw bytes saved to ROOT/design/datasheets/)

| Time (CET) | Address | Result | Saved as |
|---|---|---|---|
| 20:13:37 | https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GJM0335C1H102JB01-01A-EN_PDF_CERAMICCAPACITORSMD | HTML "The page you requested could not be found." | c76_murata_GJM0335C1H102JB01.html (first saved as .pdf, renamed .html) |
| 20:14:17 | https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM0335C1H102JE01-01A-EN_PDF_CERAMICCAPACITORSMD | PDF, 33 pages, Murata sheet GRM0335C1H102JE01 | c76_murata_GRM0335C1H102JE01.pdf and .txt (pdftotext -layout) |
| 20:14:17 | https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM033R71H102KA01-01-EN_PDF_CERAMICCAPACITORSMD | HTML "could not be found" (same command as above) | c76_murata_GRM033R71H102KA01.html (first saved as .pdf, renamed .html) |
| 20:14:58 | https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM033R71H102KA12-01A-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250813141752 | PDF, 33 pages, Murata sheet GRM033R71H102KA12 | c76_murata_GRM033R71H102KA12.pdf and .txt |
| 20:14:58 | https://datasheets.kyocera-avx.com/C0GNP0-KGM.pdf | PDF (file(1) says "0 pages"; pdftotext returned the AVX C0G (NP0) KGM text) | c76_kyocera-avx_C0GNP0-KGM.pdf and .txt |
| 20:15:09 | https://catalogs.kyocera-avx.com/SurfaceMount.pdf | PDF, catalog text garbled in the C0G table | c76_kyocera-avx_SurfaceMount-catalog.pdf and .txt |
| not captured (between 20:15:09 and 20:15:52) | https://datasheets.kyocera-avx.com/KGM-Series.pdf | HTML, not a PDF | c76_kyocera-avx_KGM-Series.html |
| 20:15:52 | https://product.samsungsem.com/mlcc/CL03C102JB3NNN.do | HTML product-search page; text does not name CL03C102 (grep count 0, saved in grep-samsung-cl03c102-count.txt) | c76_samsung_CL03C102JB3NNN.html |
| 20:15:52 | https://product.samsungsem.com/mlcc/CL03C101JB3NNN.do | HTML product page for a 100 pF part (kept, not a candidate) | c76_samsung_CL03C101JB3NNN.html |
| 20:16:19 | https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/catalog/mlcc_commercial_general_en.pdf | HTML, not a PDF (pdftotext had no input) | c76_tdk_mlcc_commercial_general_catalog.html |
| not captured (after 20:16:19) | https://product.tdk.com/en/system/files/dam/doc/product/capacitor/ceramic/mlcc/catalog/mlcc_commercial_general_en.pdf | HTML, not a PDF; overwrote the file above | c76_tdk_mlcc_commercial_general_catalog.html |

Re-checks of the addresses (`curl -sIL`, saved in url-check.txt, run after the fetches):

- GRM0335C1H102JE01-01A address: HTTP/2 200.
- GRM033R71H102KA12-01A address: HTTP/2 200.
- GRM033R71H102KA01-01-EN address: HTTP/2 403 (the earlier fetch got the "could not be found" page).
- C0GNP0-KGM address: HTTP/1.1 200 OK.
- SurfaceMount catalog address: HTTP/1.1 200 OK.
- CL03C102JB3NNN.do address: HTTP/1.1 500 Internal Server Error (the earlier fetch got a page without CL03C102).

## Searches (web search only, no page saved; raw result text not kept)

Run between about 20:12 and 20:17 CET, each with the query text below. Their results were used only to pick the addresses fetched above.

- Murata GJM0335C1H102JB01 1000pF 50V C0G 0201 datasheet
- Samsung Electro-Mechanics CL03C102 0201 C0G 1000pF 50V (two queries)
- Kyocera AVX 02013A102JAT2A 1000pF 50V C0G 0201 datasheet
- Kyocera AVX 0201 C0G 1000pF 50V (site kyocera-avx.com)
- Murata GRM033R71H102KA01 1000pF 50V X7R 0201 (site murata.com)
- Yageo CC0201 C0G 1nF 50V CC0201JRNPO9BN102 (site yageo.com)
- TDK C0603 C0G 1000pF 50V 0201 (site product.tdk.com)
- TDK 0201 C0G 1000pF 50V C0603C0G1H102 (site product.tdk.com)

## Not fetched

- Yageo: no page fetched; the search returned no part page for CC0201JRNPO9BN102.
- Murata GRM033R71H102KA01 and GJM0335C1H102JB01: "could not be found" pages, saved.
