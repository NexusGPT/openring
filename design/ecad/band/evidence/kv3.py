import pcbnew
print([n for n in dir(pcbnew) if n.startswith('DIM_UNITS') or n.startswith('DIM_SUFFIX') or n.startswith('DIM_TEXT_FRAME')])
d=pcbnew.PCB_DIM_ALIGNED(pcbnew.BOARD())
print([n for n in dir(d) if 'Unit' in n or 'Suffix' in n])
