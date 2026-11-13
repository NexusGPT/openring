import sys, os, pcbnew
lib = sys.argv[1]
for fn in sorted(os.listdir(lib)):
    if not fn.endswith('.kicad_mod'): continue
    name = fn[:-10]
    fp = pcbnew.FootprintLoad(lib, name)
    if fp is None:
        print('LOAD FAIL', name); continue
    print(name, 'pads', len(list(fp.Pads())), 'descr ok' if fp.GetLibDescription() else 'NO DESCR')
