# Checklist (W4 band flexible circuits)

Closed as `[x] ... evidence: <file>` or `[-] ... not done: <measured limit>`.

- [x] 1. band-interface.md written first, lead told by one SendMessage (section 2 final)
- [x] 2. a: land pattern J_BAND_A/B on the main board (number, net, position, size, pitch) with source per value
- [x] 3. a: tail-end pattern, fold with bend radius against the minimum
- [x] 4. a: cell tabs, protection circuit PRT1, RT1 (both pins, ground land named), motor leads (which lead on which land, cut length per size), switch lands, charging pads
- [x] 5. b: build_band.py writes flex1-us7..us13 and flex2-us7..us13 .kicad_pcb (14 files)
- [x] 6. b: flat outline length per size from the model path (function/file named, table printed)
- [x] 7. b: fold lines on a drawing layer, stiffener areas, coverlay openings, all lands, all copper lines on two layers, vias
- [x] 8. c: connectivity per board against netlist.csv (script check) for all 14 boards
- [x] 9. c: kicad-cli pcb drc --severity-all --all-track-errors: 0 violations, 0 unconnected, all 14 boards
- [x] 10. d: footprint library OpenRingBand.pretty: switch (Alps terminal numbers), motor lead lands, cell tab lands, RT1, charging pad, J_BAND_A/B board and tail; no PROVISIONAL; document and page in each description
- [x] 11. e: check_band.py exit 0 on the 14 boards (lengths within 0.05 mm of model path)
- [x] 12. e: exit 1 on broken copy 1 (swapped line)
- [x] 13. e: exit 1 on broken copy 2 (missing land)
- [x] 14. e: exit 1 on broken copy 3 (wrong length)
- [x] 15. f: fab/ Gerber and drill per board, PDF drawing per flat tail with dimensions and fold lines, folder under 20 MB
- [x] 16. g: protection circuit (what it joins, which lands) drawn or explained
- [x] 17. g: ground of RT1 drawn or explained
- [x] 18. g: path of the switch ground on FLEX1 drawn or explained
- [x] 19. h: what the model does not allow listed under "Changes other files need" (file, value now, value needed)
- [x] 20. conductor current sizing: motor start current and cell current stated, voltage drop over the longest size
- [x] 21. deferred items 30, 31, 32, 35, 37, 38, 39, 46, 118, 162, 163 each closed with a value and source
- [x] 22. conflicts list of connections.md (motor side, RT1 place, pad size) answered
- [x] 23. no word PROVISIONAL in any footprint description
- [x] 24. lists "Not closed" and "Changes other files need" in band-notes.md; last line RESULT:
- [x] 25. final audit script run on the final reply and files; output saved
- [x] 26. nothing left outside the output folder (processes, temp files) and the listing saved
