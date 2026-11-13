"""Shared: source keys, text of each page or line, quote search."""
import html, os, re, subprocess
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
D = ROOT + '/design/datasheets/'
KEYS = {'K1': 'proc_kester_np505hr_tds.pdf', 'K2': 'proc_kester_np505hr_flyer.pdf', 'K3': 'proc_kester_np505hr_product_page.txt',
        'K4': 'proc_kester_275_tds.pdf', 'K5': 'proc_kester_275_product_page.txt', 'K6': 'proc_kester_959t_tds.pdf',
        'K7': 'proc_kester_lead_free_handsoldering.pdf', 'K8': 'proc_kester_alloy_temperature_chart.pdf',
        'K9': 'proc_kester_reflow_profile_snagcu.pdf', 'T1': 'proc_ti_slua271c_qfn_son_attachment.pdf',
        'T2': 'proc_ti_snva009ai_dsbga.pdf', 'H1': 'w1_hirose_fh35c-15s-0.3shw50_drawing.pdf', 'H2': 'w1_hirose_fh35c-15s-0.3shw50_spec.pdf',
        'A1': 'slim_alps-skta-aaae010-orwin.pdf', 'N1': 'w1_knowles_spk0641ht4h-1_chipsmall.pdf', 'P1': 'npm1304_datasheet_v1_0.txt',
        'B1': 'case_bq25895.pdf', 'E1': 'case_esp32s3_mini1.pdf', 'X1': 'slim2_cs-csnp32gcr01-20260408.pdf', 'X2': 'p3_sgm38046.pdf',
        'X3': 'codes_tpd4e05u06.pdf', 'X4': 'w1_ti_sn74axc4t774.pdf', 'X5': 'motor_tlv755p.pdf', 'X6': 'w1b_murata_1269as-h-2r2m.pdf',
        'X7': 'w1_kyocera_avx_x7r_dielectric.pdf', 'X8': 'w1_kyocera_cx2016db_catalog_page10.pdf', 'X9': 'case_tps63802.pdf',
        'X10': 'w5_coilcraft_xfl4015.pdf', 'X11': 'case_kb_aptf1616.pdf', 'HW': 'w15_harwin_product_P70-6000045R.txt',
        'HP': 'p3_harwin_p70.txt', 'JL': 'w5_jlcpcb_capabilities.html'}
IMAGES = {('H1', 1): 'img/hirose_p1-1.png', ('H1', 5): 'img/hirose_p5-5.png', ('H1', 6): 'img/hirose_p6-6.png', ('B1', 64): 'img/bq_p64-64.png'}
_cache = {}
def norm(s):
    return re.sub(r'\s+', ' ', s).strip()
def units(path):
    """list of (label, text): pages for pdf, lines for others."""
    if path in _cache:
        return _cache[path]
    if path.endswith('.pdf'):
        p = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True)
        u = [('p.%d' % i, norm(t)) for i, t in enumerate(p.stdout.split('\f'), 1)]
    else:
        raw = open(path, encoding='utf-8', errors='replace', newline='').read().split('\n')
        u = []
        for i, l in enumerate(raw, 1):
            t = l
            if path.endswith('.html'):
                t = html.unescape(re.sub(r'<[^>]+>', ' ', l))
            u.append((':%d' % i, norm(t)))
    _cache[path] = u
    return u
def find(path, quote):
    q = norm(quote)
    return [lab for lab, t in units(path) if q in t]
CITE = re.compile(r'\{(?P<src>[A-Z]+\d*|design/[^ "{}]+) (?:(?P<img>p(?P<pg>\d+) image)|"(?P<q>[^"]+)")\}')
