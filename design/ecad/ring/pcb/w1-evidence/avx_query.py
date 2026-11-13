# Query the Kyocera AVX capacitance-range tables: avx_query.py <pdf> <value_uF as printed, e.g. 0.1 or 2.2> -> size, voltage, thickness code
import fitz, sys, warnings
warnings.filterwarnings('ignore')
doc = fitz.open(sys.argv[1]); want = sys.argv[2]
for pn in range(len(doc)):
    ws = doc[pn].get_text('words')
    sizes = [w for w in ws if w[4] in ('0101*','0201','0402','0603','0805','1206','1210') and w[1] < 700]
    hdr_y = sorted(set(round(w[1]) for w in sizes))
    for w in ws:
        if w[4] != want or w[0] > 100: continue
        y = w[1]
        # table header = nearest size-header row above this row, WVDC row = nearest WVDC word row above
        above = [h for h in hdr_y if h < y]
        if not above: continue
        hy = max(above)
        wv = max((x for x in ws if x[4] == 'WVDC' and x[1] < y), key=lambda x: x[1], default=None)
        if wv is None: continue
        volts = [(x[0], x[4]) for x in ws if abs(x[1]-wv[1]) < 3 and x[4].replace('.','',1).isdigit()]
        sz = [(h[0], h[4]) for h in sizes if abs(h[1]-hy) < 3]
        # thickness key letters under the table
        marks = [(x[0], x[4]) for x in ws if abs(x[1]-y) < 3 and x[0] > 100 and x[4] in list('ABCEGJKMNPQXYZ')]
        for mx, mk in marks:
            v = min(volts, key=lambda t: abs(t[0]-mx))[1]
            s = min(sz, key=lambda t: abs(t[0]-mx))[1]
            print('page %d: %s uF -> size %s, %s V, thickness code %s' % (pn+1, want, s, v, mk))
