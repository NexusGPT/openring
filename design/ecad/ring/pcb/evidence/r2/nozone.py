# nozone.py in.kicad_pcb out.kicad_pcb: copy without zone fills (for pictures that show the tracks)
import re, sys, shutil
t = open(sys.argv[1]).read(); out = re.sub(r'\(filled_polygon.*?\n\t\t\)\n', '', t, flags=re.S); open(sys.argv[2], 'w').write(out)
for ext in ('.kicad_pro', '.kicad_dru'):
    shutil.copy(sys.argv[1][:-10] + ext, sys.argv[2][:-10] + ext) if __import__('os').path.exists(sys.argv[1][:-10] + ext) else None
