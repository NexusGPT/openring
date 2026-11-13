#!/bin/bash
# One logged pass over the maker and distributor addresses tried for the Not closed items (second look; the first looks were
# in the working session and are not saved). Output: HTTP code, bytes, content type, and the first bytes' file type.
# No name, company or e-mail is sent: a generic browser-like User-Agent only.
S=<scratch>/dl
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
while read -r name url; do
  [ -z "$name" ] && continue
  out="$S/fa_$name.out"
  res=$(curl -sS -L -A "$UA" --max-time 25 -o "$out" -w "%{http_code} %{size_download} %{content_type}" "$url" 2>&1 | tail -1)
  ft=$(file -b "$out" 2>&1 | cut -c1-40)
  echo "$name | $res | $ft | $url"
done <<'LIST'
murata_dfe201610e https://www.murata.com/en-global/products/productdetail?partno=DFE201610E-2R2M%3DP2
murata_catalog_c02e https://www.murata.com/products/catalog/pdf/c02e.pdf
tdk_mlz1608 https://product.tdk.com/en/search/inductor/inductor/smd/info?part_no=MLZ1608M2R2WT000
samsung_cl05 https://weblib.samsungsem.com/mlcc/pdf/CL05A105KA5NQNC.pdf
coilcraft_xfl2010 https://www.coilcraft.com/en-us/products/power/shielded-inductors/ultra-low-profile/xfl/xfl2010/
mouser_dfe https://www.mouser.com/ProductDetail/Murata-Electronics/DFE201610E-2R2MP2
digikey_dfe https://www.digikey.com/en/products/detail/murata-electronics/DFE201610E-2R2M-P2/5233689
lcsc_search https://wmsc.lcsc.com/ftps/wm/search/global?keyword=GRM155R61E105KA12D
nordic_csp61 https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/chapters/mec_spec.html-csp61_package
knowles_spk0641 https://www.knowles.com/products/microphones/mems-microphones/spk0641ht4h-1
vishay_ntc https://www.vishay.com/docs/33023/ntcs0402e3.pdf
yageo_rc https://www.yageo.com/upload/media/product/products/datasheet/rchip/PYu-RC_Group_51_RoHS_L_12.pdf
LIST
