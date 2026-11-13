import pcbnew
print([n for n in dir(pcbnew) if 'IO' in n][:40])
