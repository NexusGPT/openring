import csv, io, re
B = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/bom.csv")
t = open(B, newline='').read()
rows = list(csv.reader(io.StringIO(t)))
H = rows[0]
ix = {h: i for i, h in enumerate(H)}
body = rows[1:]

def find(ref):
    m = [r for r in body if r[ix['reference']].replace(' ', '') == ref]
    assert len(m) == 1, (ref, len(m))
    return m[0]

def setf(r, **kw):
    for k, v in kw.items():
        r[ix[k]] = v

TONPM = 'to confirm against the nPM1304 product specification (S18)'

# (a) U2 -> nPM1304
setf(find('U2'), item='Power chip', function='charger, 2 buck rails, 2 load switches, ship mode (Nordic nPM1304, architecture 17.13)',
     maker_part_number='', package='CSP-35 (package code CA)', size_mm='3.1 x 2.4',
     key_figures='nPM1304 replaces the nPM1300 (review F05): charge current 4 to 100 mA in 0.5 mA steps, termination voltage 3.6 to 4.65 V in 50 mV steps, 2 buck 200 mA 1.0 to 3.3 V, 2 load switches 100 mA or LDO 50 mA, ship mode 370 nA (product page summary); charge setting 15 mA and 4.35 V (4.35 V is on the 50 mV grid, not named as an option by Nordic); ball map against the nPM1300 not confirmed, every U2 ball provisional',
     evidence='LIST',
     source_file_or_url='https://www.nordicsemi.com/Products/nPM1304 ; https://docs.nordicsemi.com/r/bundle/ps_npm1304/page/keyfeatures_html5.html ; design/parts/research-npm1304.md sections 1 to 3',
     unit_price_and_currency_at_qty1='',
     open_action='S18: Nordic must answer: the orderable part number (order code left empty here), the ball map of the 35-ball CSP against the nPM1300, whether 4.35 V is a selectable termination voltage, the termination current options, the passives and the two resistor-set supplies of the nPM1304 (architecture 17.9 S18, 17.13)')
# resistor-set supplies and the other passives follow the nPM1300 kit design: marked
for ref, what in (('R71', 'VSET1'), ('R72', 'VSET2')):
    r = find(ref)
    setf(r, item='Power chip %s resistor' % what, open_action='%s: the value is Nordic\'s nPM1300 reference configuration 1; the nPM1304 page read gives none' % TONPM)
for ref in ('C71', 'C73', 'C74, C75, C78, C79'.replace(' ', ''), 'C76,C77', 'L71,L72', 'RT1'):
    r = find(ref)
    for k in ('item', 'function'):
        r[ix[k]] = r[ix[k]].replace('nPM1300 ', 'U2 ')
    r[ix['function']] = r[ix['function']] + '; value from the nPM1300 kit design (DK PCA10184); ' + TONPM
    oa = r[ix['open_action']]
    r[ix['open_action']] = (oa.replace('nPM1300', 'power chip') + '; ' if oa else '') + TONPM
r = find('C61,C72,C80')
setf(r, item='Schematic addition: 100 nF at storage supply (C61), U2 VBUS (C72), U2 VDDIO (C80), U10 supplies (C81, C82)',
     reference='C61,C72,C80,C81,C82', quantity='5',
     function='100 nF: storage supply (W3), U2 VBUS and VDDIO (nPM1300 kit design, ' + TONPM + '), U10 VCCA and VCCB (TI SN74AXC4T774 datasheet SCES898C section 8, 0.1 uF)',
     open_action='C72 and C80: ' + TONPM)
# F07 level shifter
new = [''] * len(H)
setf(new, item='Level shifter, storage bus', reference='U10', quantity='1',
     function='SPI bus between the 1.8 V main chip and the 3.0 V storage part: SD_SCK, SD_MOSI, SD_CS from 1.8 V to 3.0 V (A to B), SD_MISO from 3.0 V to 1.8 V (B to A); VCCA on VDD_1V8, VCCB on VDD_SD; all ports Hi-Z while VDD_SD is below 100 mV (review F07, sch-notes A6)',
     maker='Texas Instruments', maker_part_number='SN74AXC4T774RSVR', package='UQFN-16 (RSV)', size_mm='2.6 x 1.8',
     key_figures='4-bit dual-supply translator, 0.65 to 3.6 V on each port, independent DIR pins, up to 310 Mbps 1.8 V to 3.3 V, 3000 per reel, status Active Production (TI SCES898C, saved copy evidence/a6/ti_sn74axc4t774.txt)',
     evidence='DS',
     source_file_or_url='https://www.ti.com/lit/ds/symlink/sn74axc4t774.pdf ; design/ecad/ring/evidence/a6/ti_sn74axc4t774.txt',
     open_action='NEW-12: a distributor must answer: price and stock of SN74AXC4T774RSVR (not read); the lead confirms the level shifter choice (sch-notes A6 open point O3); the board owner must place the 2.6 x 1.8 mm part and C81, C82')
i = body.index(find('U3')) + 1
body.insert(i, new)

# (h) microphone
setf(find('U5,U6'),
     function='PDM microphone, bottom port, one stereo input (architecture 16.6)',
     key_figures='Infineon IM68D128B product brief (design/datasheets/mic-research/im68d128b-brief.txt): SNR 67.5 dB(A), 580/190 uA (HPM/LPM), supply 1.62 to 3.60 V, bottom port, acoustic port diameter 0.325 mm; 22 mm apart on the X axis (architecture 16.4); the order code is the part number in a DigiKey URL seen in search text (bench-kits.md section 3), IM68D128B datasheet not saved')

# (b) one control
setf(find('SW1,SW3,SW4,SW5'),
     item='Joystick switches x4',
     function='4 directions under the joystick nub: toward fingertip, toward hand, up, down (architecture 17.3, 17.11); the centre press is the switch SW2 under the nub\'s centre',
     key_figures='1.6 +/-0.5 N, travel 0.11 mm, 300,000 presses, IP6X and IPX7, 12 V 50 mA max; outline 2.6 x 1.6 x 0.53 is search text (LCSC), land pattern not in the document; in a cross at 2.1 mm from the nub centre, footprint 5.8 x 5.8 (architecture 17.3; at 1.9 mm the four switches overlap by 0.2 mm)')
setf(find('SW2'),
     item='Joystick centre switch (the former record button; no record button remains)',
     function='1 switch under the centre of the joystick nub, on net BTN_REC: a long press of 1.0 s starts and stops a recording, a short press while recording marks a highlight (architecture 17.11); second choice if it does not fit between the four direction switches: two opposite direction switches closing within 40 ms (16.5, bench item B6)',
     key_figures='same part as the joystick switches (1.6 N, 0.11 mm travel, 300,000 presses)')
setf(find('M1'),
     function='haptic motor in a shoulder of the band; its place is measured again in the inside model rebuild (architecture 17.11, 17.12; 17.10 gave +51 degrees); FPC tail to flex tail A (joystick side) by the BAND_SPLIT table of make_netlist.py, confirmed by the lead after the inside model')
setf(find('R41'), key_figures='(3.0 V - 2.0 V) / 680 ohm = 1.5 mA (architecture W5; 2.0 V typical from Kingbright\'s 2013 preliminary sheet)')
r = find('BT1')
setf(r, function='custom curved cell in the band, 4.35 V; 17.10 gave -39 degrees through the bottom to +167 degrees (154 degrees of arc), measured again in the rebuild (architecture 17.11, 17.12)',
     key_figures='273 cubic mm x 0.054 to 0.072 mAh per cubic mm (architecture 17.10); 4.35 V; charge 15 mA (1 C of the smallest cell of the range) with the nPM1304 until Grepow states its own limit (architecture 17.13, S12); shorter per smaller ring size',
     open_action='S12: Grepow must answer: can it build the curved cell 1.6 x 6.0 x 28.4 mm on its centre line (17.10) at 4.35 V, its order code, price, and the highest charge current it accepts (the nPM1304 sets 4 to 100 mA)')
setf(find('PRT1'), function='protection circuit on the cell\'s tab, inside the cell envelope; 17.10 put it from -35 to -27 degrees, measured again in the rebuild (architecture 17.11)',
     size_mm='1.5 x 5')
setf(find('HSG1'),
     function='one metal body: block 29.3 x 14.75 mm in plan, 3.85 mm high at the centre line and 2.95 mm at the long edges, with the 8.0 mm wide band, 2.6 mm thick, 3.6 mm at the shoulders (19 to 61 degrees) and at the joystick (zone measured again in the rebuild, architecture 17.11), inner diameter by ring size (18.95 mm at US 9); 7 sizes US 7 to 13 as files',
     key_figures='plan corner radius 2.5; glass face curved across the finger, arc radius 30.7; shell 0.5 mm outside and 0.6 mm at each edge, channel 6.8 mm wide; openings: 2 microphone slots 1.2 x 0.3, 2 floor slots, joystick frame 6.4 x 5.4 on the outer face at 78 degrees on the joystick side (architecture 17.11); no record opening; no pad holes: the 4 charging pads are on the inside face of the band in the resin liner (architecture 17.12); material not fixed (titanium or stainless steel, architecture 16.10)')
setf(find('U9'), function='W7 USB protection array for VBUS, D+, D- (architecture W7; \'protection parts\' unchanged in 17.4); placement on the main board beside the J_BAND_B pads (no contact board); the charging pads touch the skin (architecture 17.12)',
     open_action='NEW-10: a distributor must answer: whether the suffix of TPD4E05U06DQAR is the orderable code of the DQA package (copied from the TI listing). The ring electronics designer must place it, since the contact board is removed')
setf(find('CP1,CP2,CP3,CP4'),
     function='charging pads on the INSIDE face of the band at the point opposite the block (180 degrees), in a row around the band, in the resin liner and not in the metal body, gold-plated flush with the liner, order VBUS, D-, D+, GND (architecture 17.12)',
     key_figures='4 pads, 1.6 mm pitch (17.3; pitch and size follow the case pin, measured in the rebuild); wired in flex tail B (other side); the pebble case (17.12) mates with them',
     open_action='Design partner (ring maker) must answer: pad part or plating, how the pads are set in the resin liner and wired to the tail, and the mating contact of the case')
setf(find('J_BAND_A'), function='solder pads for flex tail A (joystick side): 4 direction switches, centre switch SW2, motor 2, ground = 8 pads (BAND_SPLIT table of make_netlist.py; architecture 17.8 as replaced by 17.11 and 17.12)', package='SOLDER_PADS_1x8', value='8 wire pads')
setf(find('J_BAND_B'), function='solder pads for flex tail B (other side): cell 2, temperature sensor 1, charging pads 4 = 7 pads (BAND_SPLIT table of make_netlist.py)', package='SOLDER_PADS_1x7', value='7 wire pads')
setf(find('FLEX1'), item='Flex tail A (joystick side)',
     function='band flex from the main board to the joystick-side shoulder: 4 direction switches, centre switch SW2, motor 2, ground; 0.15 mm flex; through a floor slot (split confirmed by the lead after the inside model)',
     key_figures='8 conductors; outline not drawn')
setf(find('FLEX2'), item='Flex tail B (other side)',
     function='band flex from the main board to the cell, its temperature sensor and the 4 charging pads: 7 conductors, through the floor slot into the other shoulder',
     key_figures='7 conductors; outline not drawn',
     open_action='Design partner or a flex maker must answer: outline drawing, stack and quote (no drawing exists); who solders the cell tab and the pads')
r = find('CAP1')
setf(r, item='Joystick cap',
     function='rounded rectangular nub with its flange (one moulded part) over the 4 direction switches, in a raised frame, on the outer face of the band at 78 degrees on the joystick side; the switch SW2 sits under the nub\'s centre (architecture 17.11)',
     key_figures='switches in a cross at 2.1 mm from the centre (architecture 17.3); stack liner 0.3, flex 0.15, switch 0.53, flange 0.4, shell 0.5 = 3.1 inside (17.3 gave 3.6 inside at the shoulder); bench B9')
# CAP2 removed
cap2 = find('CAP2')
body.remove(cap2)
# references: one token each, no spaces
for r in body:
    r[ix['reference']] = r[ix['reference']].replace(', ', ',').replace(' ', '')
o = io.StringIO()
csv.writer(o, lineterminator='\n').writerows([H] + body)
open(B, 'w', newline='').write(o.getvalue())
print('lines', len(body))
