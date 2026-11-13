#!/usr/bin/env python3
"""check_footprints.py [library.pretty [netlist.csv [footprint-sources.csv]]]   run with pcb/run_kipy.sh (KiCad's own Python).

For every part of the netlist (every reference of ../parts.csv) it loads the footprint named there from the library with
KiCad's pcbnew and fails (exit 1) when
  1 the footprint cannot be loaded from the library,
  2 a pin of the netlist (reference, pin_number) has no pad of that name,
  3 the pad count differs from footprint-sources.csv (or the reference has no row there),
  4 the footprint description holds the word PROVISIONAL, or names no document file,
  5 the library holds a footprint no part uses (one file per distinct package), or a pad name other than MP repeats.
Band parts (footprint library OpenRingBand, drawn by band-circuits in ecad/band/OpenRingBand.pretty) are read from that library: every
netlist pin must be a pad of it, the pad count must equal footprint-sources.csv, and a missing footprint file fails (round 2).
Exit 0 and the last line 'RESULT PASS ...' when all hold.
"""
import csv, os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
RING = os.path.dirname(HERE)
lib = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'OpenRing.pretty')
net_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RING, 'netlist.csv')
src_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'footprint-sources.csv')

fails = []
BAND_LIB = os.path.join(os.path.dirname(os.path.dirname(RING)), 'ecad', 'band', 'OpenRingBand.pretty') if False else os.path.join(os.path.dirname(RING), 'band', 'OpenRingBand.pretty')
not_delivered, notes_ = [], []
if len(sys.argv) > 4:
    BAND_LIB = sys.argv[4]


def fail(msg):
    fails.append(msg)
    print('FAIL', msg)


def rows(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


parts = rows(os.path.join(RING, 'parts.csv'))
netlist = rows(net_path)
sources = {r['reference']: r for r in rows(src_path)}
pins = {}
for r in netlist:
    pins.setdefault(r['reference'], []).append(r['pin_number'])

cache = {}
band_ok = []
used = set()
n_pins = 0
for p in parts:
    ref = p['reference']
    flib, lname = p['footprint'].split(':', 1)
    if flib == 'OpenRingBand':
        if not os.path.exists(os.path.join(BAND_LIB, lname + '.kicad_mod')):
            not_delivered.append('%s (%s)' % (ref, lname))
            fail('%s: band footprint %s is not in %s (not yet delivered is not accepted)' % (ref, lname, BAND_LIB))
            continue
        bfp = pcbnew.FootprintLoad(BAND_LIB, lname)
        bpads = [pd.GetNumber() for pd in bfp.Pads()]
        row = sources.get(ref)
        if row is None:
            fail('%s has no row in footprint-sources.csv' % ref)
        elif int(row['pad_count']) != len(bpads):
            fail('%s: band footprint %s has %d pads, footprint-sources.csv says %s' % (ref, lname, len(bpads), row['pad_count']))
        if re.search('provisional', bfp.GetLibDescription(), re.I):
            fail('%s: description of band footprint %s holds PROVISIONAL' % (ref, lname))
        for pn in pins.get(ref, []):
            n_pins += 1
            if pn not in bpads:
                fail('%s pin %s has no pad of that name in band footprint %s (pads: %s)' % (ref, pn, lname, ' '.join(bpads)))
        band_ok.append(ref)
        continue
    used.add(lname)
    if lname not in cache:
        cache[lname] = pcbnew.FootprintLoad(lib, lname)
    fp = cache[lname]
    if fp is None:
        fail('%s: footprint %s not found in %s' % (ref, lname, lib))
        continue
    pads = [pd.GetNumber() for pd in fp.Pads()]
    padset = set(pads)
    for pn in pins.get(ref, []):
        n_pins += 1
        if pn not in padset:
            fail('%s pin %s has no pad of that name in %s (pads: %s)' % (ref, pn, lname, ' '.join(sorted(padset))))
    row = sources.get(ref)
    if row is None:
        fail('%s has no row in footprint-sources.csv' % ref)
    else:
        if int(row['pad_count']) != len(pads):
            fail('%s: %s has %d pads, footprint-sources.csv says %s' % (ref, lname, len(pads), row['pad_count']))
        if row['footprint'] != lname:
            fail('%s: footprint-sources.csv names %s, parts.csv names %s' % (ref, row['footprint'], lname))
    d = fp.GetLibDescription()
    if re.search('provisional', d, re.I):
        fail('%s: description of %s holds PROVISIONAL' % (ref, lname))
    if not re.search(r'\.(pdf|md|csv)', d):
        fail('%s: description of %s names no document file' % (ref, lname))
    dup = sorted(n for n in padset if n != 'MP' and pads.count(n) > 1)
    if dup:
        fail('%s: %s repeats pad names %s' % (ref, lname, dup))

lib_files = sorted(f[:-10] for f in os.listdir(lib) if f.endswith('.kicad_mod'))
for name in lib_files:
    if name not in used:
        fail('library holds %s, which no part uses' % name)

for n in notes_:
    print('NOTE', n)
if not_delivered:
    print('not yet delivered (band library): ' + ' '.join(not_delivered))
print('band parts read from the band library: %d, not yet delivered: %d' % (len(band_ok), len(not_delivered)))
print('%d parts, %d footprints loaded, %d netlist pins checked against pads, %d library files' % (len(parts), len(cache), n_pins, len(lib_files)))
if fails:
    print('RESULT FAIL %d footprints netlist %s library %s' % (len(fails), os.path.basename(net_path), os.path.basename(lib)))
    sys.exit(1)
print('RESULT PASS %d parts, %d footprints, %d pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL' % (len(parts), len(cache), n_pins))
