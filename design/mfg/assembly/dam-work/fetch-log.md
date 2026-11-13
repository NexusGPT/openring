# Fetch log: dam material sheets (researcher helper)

Client: plain HTTP GET with curl, user agent "Mozilla/5.0". No login, no form, no browser, no contact with a supplier, no purchase. Times are from `date` (CET) at the start of each command. A WebFetch or WebSearch call is not timed by `date` and is marked "not timed".

## Saved as a datasheet (product sheet on the maker's own host)

| time (CET) | address fetched | result | saved as |
|---|---|---|---|
| 2026-11-13 19:11:43 | https://p1.aprimocdn.net/dymax/1adddf7f-a5c2-4e59-add7-b4ef005640c7/_Original%20file.pdf (Dymax PDS 9014; linked from https://dymax.com/products/formulations/light-curable-materials/encapsulating/9014) | 200 application/pdf, 353069 bytes | design/datasheets/dam_dymax_9014.pdf and dam_dymax_9014.txt |
| 2026-11-13 19:12:15 | https://dymax.com/content/download/7137/86006?version=1 (Dymax PDS 9422-SC) | 200 application/pdf, 970144 bytes | design/datasheets/dam_dymax_9422-sc.pdf and dam_dymax_9422-sc.txt |
| 2026-11-13 19:13:13 | https://datasheets.tdx.henkel.com/LOCTITE-SI-5240-en_GL.pdf (Henkel TDS LOCTITE SI 5240, September 2020) | 200 application/pdf, 167735 bytes | design/datasheets/dam_henkel-loctite_si-5240.pdf and dam_henkel-loctite_si-5240.txt |
| 2026-11-13 19:13:13 | https://www.hoenle.com/wp-content/uploads/Vitralit-UD-8060-F-english-tds-hoenle-adhesive.pdf (TDS Vitralit UD 8060 F, issued by Hoenle Adhesives GmbH; see note 2) | 200 application/pdf, 218366 bytes | design/datasheets/dam_panacol_vitralit-ud8060f.pdf and dam_panacol_vitralit-ud8060f.txt |
| 2026-11-13 19:13:28 | https://datasheets.tdx.henkel.com/LOCTITE-ABLESTIK-UV300X-en_GL.pdf (Henkel TDS LOCTITE ABLESTIK UV300X, December-2016) | 200 application/pdf, 84956 bytes | design/datasheets/dam_henkel-loctite_uv300x.pdf and dam_henkel-loctite_uv300x.txt |

## Fetched, a PDF, but not a product sheet (kept, renamed)

| time (CET) | address | result | file |
|---|---|---|---|
| 2026-11-13 19:10:59 | https://dymax.com/content/download/7374/86717?version=1 | 200 application/pdf, 1764653 bytes; an application study on light-cure encapsulants (dam and fill, moisture cure), not the 9014 product sheet | design/datasheets/dam_dymax_encapsulant-study.pdf and .txt (first saved as dam_dymax_9014.pdf and .txt; renamed at 19:11:43) |

## Refused, missing, or not a sheet (kept as the bytes received, renamed; not retried)

| time (CET) | address | result | file |
|---|---|---|---|
| 2026-11-13 19:10:59 | https://www.delo.de/fileadmin/files/instructions/en/delo_dualbond__gebr-en_.pdf (a guessed DELO path) | 404, text/html | design/datasheets/dam_delo_eg4797.fetch-404.html (first saved as dam_delo_eg4797.pdf; renamed at 19:11:43) |
| 2026-11-13 19:12:15 | https://www.masterbond.com/tds/uv22dc80-10f | 403, text/html | design/datasheets/dam_masterbond_uv22dc80-10f.fetch-403.html. Not retried. |
| 2026-11-13 19:12:15 | https://www.epotek.com/docs/en/Datasheet/OG116-31.pdf | 200 text/html, redirected to https://meridianadhesives.com/products/epo-tek-og116-31/ (a distributor page) | design/datasheets/dam_epotek_og116-31.redirect-html.html (renamed at 19:12:27) |
| 2026-11-13 19:12:15 | https://www.epotek.com/docs/en/Datasheet/MED-OG116-31.pdf | 200 text/html, redirected to the same distributor page | design/datasheets/dam_epotek_med-og116-31.redirect-html.html (renamed at 19:12:27) |
| 2026-11-13 19:12:27 | https://www.epotek.com/docs/en/Datasheet/OG116.pdf (redirects not followed) | 301 to https://meridianadhesives.com/products/epo-tek-og116/ | design/datasheets/dam_epotek_og116.redirect-html.html |
| 2026-11-13 19:12:27 | https://www.epotek.com/docs/en/Datasheet/MED-OG116-31.pdf (redirects not followed) | 301 to https://meridianadhesives.com/products/epo-tek-og116-31/ | design/datasheets/dam_epotek_med-og116-31.redirect-html.html (the file of the earlier 19:12:15 fetch was overwritten by this one) |
| 2026-11-13 19:12:56 | https://www.mouser.com/datasheet/2/773/LOCTITE_ABLESTIK_UV300X_en_GL-3434263.pdf | 200 text/html, not a PDF (a Mouser page) | design/datasheets/dam_henkel-loctite_ablestik-uv300x.mouser-html.html. A text copy written from it was removed at 19:13:28 (note 3). |

## Plain WebFetch of web pages (not timed by date; bytes not saved)

- https://dymax.com/products/formulations/light-curable-materials/encapsulating/9014 (product page; gave the PDS link)
- https://www.delo-adhesives.com/en/downloads/ (no EG4797 link)
- https://portal.delo.de/datasheets (no list of sheets visible; no EG4797 sheet)

## Search results used only as leads (no sheet saved from them; not timed by date)

- Searches for dam-type and thixotropic light-cure products (Dymax, DELO DUALBOND, Master Bond, EPO-TEK, Henkel Loctite, Panacol).

## Notes

1. The requests carry no name, company, e-mail, project name or address. The user agent is "Mozilla/5.0".
2. The Vitralit UD 8060 F sheet names Hoenle Adhesives GmbH as its issuer (p.5 l.258). The line "Vitralit" as the product line comes from a search result title, not from the sheet. The Panacol host was not reached, so the file name keeps the product line name.
3. This run wrote a text copy (dam_henkel-loctite_ablestik-uv300x.txt) from the Mouser HTML page and removed it with `rm -f` at 19:13:28, because it was not a datasheet. It is the only file this run deleted.
4. Renames (`mv`) keep names true to content: dam_dymax_9014 (first held the Dymax study), dam_delo_eg4797 (404 HTML), dam_epotek_* (301 HTML), dam_masterbond_uv22dc80-10f (403 HTML).
