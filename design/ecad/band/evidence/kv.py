import pcbnew
print(pcbnew.Version(), pcbnew.GetBuildVersion())
print([n for n in dir(pcbnew) if 'Footprint' in n and ('Save' in n or 'Load' in n or 'Plugin' in n)])
