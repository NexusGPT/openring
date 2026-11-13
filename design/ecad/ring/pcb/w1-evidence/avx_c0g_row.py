# Which sizes and voltages does the Kyocera AVX C0G (NP0) table offer at 0.1 uF?  (w1_kyocera_avx_c0g_dielectric.pdf page 3)
import fitz, warnings
warnings.filterwarnings('ignore')
doc = fitz.open((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/w1_kyocera_avx_c0g_dielectric.pdf"))
ws = doc[2].get_text('words')
sizes = [w for w in ws if w[4] in ('0201', '0402', '0603', '0805', '1206') and abs(w[1] - 107) < 3]
size_x = sorted((w[0], w[4]) for w in sizes)
wvdc = [w for w in ws if w[4] == 'WVDC' and w[1] < 300][0]
volts = sorted((w[0], w[4]) for w in ws if abs(w[1] - wvdc[1]) < 3 and w[4].replace('.', '', 1).isdigit())
row = [w for w in ws if w[4] == '0.1' and w[0] < 100 and w[1] > 400][0]
marks = sorted((w[0], w[4]) for w in ws if abs(w[1] - row[1]) < 3 and w[0] > 100)
def grp(x):
    return min(size_x, key=lambda t: abs(t[0] - x))[1]   # nearest size header centre
for x, m in marks:
    v = min(volts, key=lambda t: abs(t[0] - x))[1]
    print('0.1 uF C0G: size %s, %s V, thickness code %s' % (grp(x), v, m))
for w in ws:
    if w[4] in ('Max.',) and w[1] > 400:
        pass
print('thickness code X = 2.29 mm max (key under the table, page 3 line "Letter ... Max. Thickness")')
