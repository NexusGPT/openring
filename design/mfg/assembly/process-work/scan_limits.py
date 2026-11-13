"""Scan saved maker documents of the parts that pass through a reflow for reflow limits. Writes logs/scan_limits.log."""
import re, subprocess, os
D = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/datasheets")
W = os.path.dirname(os.path.abspath(__file__))
FILES = {'U3': 'slim2_cs-csnp32gcr01-20260408.pdf', 'U4': 'p3_sgm38046.pdf', 'U9': 'codes_tpd4e05u06.pdf',
         'U10': 'w1_ti_sn74axc4t774.pdf', 'X1': 'w1_kyocera_cx2016db_catalog_page10.pdf', 'X2': 'w1_txc_9ht11_datasheet.pdf',
         'ANT1': 'antenna_johanson_2450AT18D0100001E_8p.pdf', 'L10,L71,L72': 'w1b_murata_1269as-h-2r2m.pdf',
         'C71': 'w1b_murata_grm155r61e105ka12.pdf', 'C88': 'w1c_murata_grt188r61a106ke13.pdf',
         'C83,C4,C25,C22': 'w1d_murata_grm155r60j106me15.pdf', 'C84,C11,C21,C26,C27': 'w1d_murata_grm155r61a475meaa.pdf',
         'C60,C85': 'w1_kyocera_avx_x7r_dielectric.pdf', 'C35,C36': 'w1_kyocera_avx_c0g_dielectric.pdf',
         'U11': 'motor_tlv755p.pdf', 'U5,U6': 'w1_knowles_spk0641ht4h-1_chipsmall.pdf'}
pat = re.compile(r'reflow|peak|260|245|250|MSL|moisture|J-STD-020|soldering heat|cycles', re.I)
with open(os.path.join(W, 'logs', 'scan_limits.log'), 'w') as out:
    for ref, f in FILES.items():
        p = subprocess.run(['pdftotext', '-layout', os.path.join(D, f), '-'], capture_output=True, text=True)
        pages = p.stdout.split('\f')
        hits = 0
        for i, pg in enumerate(pages, 1):
            for ln in pg.split('\n'):
                if pat.search(ln) and not re.search(r'peak current|peak.to.peak|Peak gain', ln, re.I):
                    out.write('%s | %s p%d | %s\n' % (ref, f, i, ln.strip()[:180]))
                    hits += 1
        out.write('%s | %s | pages %d hits %d stderr %s\n' % (ref, f, len(pages) - 1, hits, p.stderr.strip()[:100]))
