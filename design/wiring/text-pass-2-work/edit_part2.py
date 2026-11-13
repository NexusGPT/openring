import sys
R=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
def sub(path, lineno, old, new):
    p=R+path
    L=open(p,encoding='utf-8').read().split('\n')
    s=L[lineno-1]
    assert s.count(old)==1,(path,lineno,old,s.count(old))
    L[lineno-1]=s.replace(old,new)
    open(p,'w',encoding='utf-8').write('\n'.join(L))
    print('OK',path,lineno)
# 71
sub('requirements.md',195,
 'The constant-current part alone then takes 82 to 109 minutes [CALC: 20.4 / 15 and 27.2 / 15 hours], so 90 minutes is not met for the larger cell at this setting.',
 'REPLACED (2026-11-13; old cell sizes of 20.4 to 27.2 mAh). Do not use: ~~The constant-current part alone then takes 82 to 109 minutes [CALC: 20.4 / 15 and 27.2 / 15 hours]~~. Per size, from `design/mfg/specs/cell.md` line 63 [CALC, firmware F6 8.1]: the constant-current part alone takes 1.17 to 1.57 hours at US 7 and 1.59 to 2.13 hours at US 13, so 90 minutes is not met for the larger cell at this setting.')
# 121
sub('requirements.md',204,
 '22. **S6 Water and dust, IP65 or better: NOT MET ON PAPER (2026-11-11).**',
 '22. **Record of 2026-11-11, REPLACED by line 26 (S6) and by item 3 of the section "Changes after sign-off: owner decisions of 2026-11-13" (splash and sweat resistant as a goal; no rating claimed; the spray test of assembly step 25 is the pass line). Do not use the IP65 wording below.** S6 Water and dust, IP65 or better: NOT MET ON PAPER (2026-11-11).')
# 11
sub('design/mfg/specs/main-board.md',18,
 'Open (point 3): surface finish and solder-mask colour are not stated. The 3D model shows gold pad rectangles on a solder-mask face (design/mech/thin/thin-notes.md); that is the modeller\'s assumption.',
 'Surface finish ENEPIG; solder mask green on both sides, U1 and U2 land openings equal to the land (source: design/ecad/ring/pcb/fab/stackup.txt line 20; open point 3 closed). Before: "not stated"; the 3D model shows gold pad rectangles on a solder-mask face (design/mech/thin/thin-notes.md), the modeller\'s assumption.')
sub('design/mfg/specs/main-board.md',56,
 '3. Surface finish and solder-mask colour: the board maker proposes, the design partner accepts.',
 '3. CLOSED 2026-11-13: surface finish ENEPIG, solder mask green on both sides (`design/ecad/ring/pcb/fab/stackup.txt` line 20). Before: the board maker proposes, the design partner accepts.')
# 156
sub('design/architecture.md',303,
 'full-speed USB host in the case, 6.3 minutes per recorded hour',
 'full-speed USB host in the case, REPLACED by `design/firmware.md` line 718 and `design/case/case-architecture.md` line 88 (3.21 minutes per recorded hour, 2 microphones). Do not use: ~~6.3 minutes per recorded hour~~')
# 158
sub('design/architecture.md',153,
 '| Record button | +4.0 |',
 '| Record button: REPLACED by section 17.11 (the record button is removed; one control, the joystick; a long press of its centre records). Do not use: ~~Record button~~ | +4.0 |')
sub('design/architecture.md',229,
 '- Record button (owner, 2026-11-10: recording "only when a long press on it"):',
 '- REPLACED by section 17.11 (the record button is removed; one control, the joystick; a long press of its centre records). Do not use: Record button (owner, 2026-11-10: recording "only when a long press on it"):')
# 103
sub('design/architecture.md',162,
 '- Join: 4 screws M1.2 x 3 from below, at the corners, and a 0.5 mm silicone gasket in a groove.',
 '- Join: REPLACED by `design/wiring/lead-decisions.md` line 57 (row "adhesive code, switch code, screw (items 45, 100, 103)": "The M1.2 screw is no longer in the design (not in the model, not in the parts list)"). Do not use: ~~4 screws M1.2 x 3 from below, at the corners~~; and a 0.5 mm silicone gasket in a groove.')
# 147
sub('design/mech/light-path/light-path.md',1,
 'history: the recording light is removed in v7 (architecture 17.30)',
 'history: the recording light was removed in design version 7 (architecture 17.30; `design/architecture.md` line 523) and this file is history')
# 161
sub('design/supplier-package/make_one_pager.py',64,
 'Not ready: the circuit board layout (who routes it is not decided), the software code, a working sample.',
 'Not ready: the software code, a working sample, a built and tested circuit board (the layout is routed and passes its rules check with 0 unconnected items).')
sub('design/supplier-package/make_one_pager.py',99,
 '尚未完成：电路板布线（由谁布线尚未决定）、软件代码、可工作的样机。',
 '尚未完成：软件代码、可工作的样机、已制造并测试的电路板（电路板布线已完成，设计规则检查无未连接项）。')
