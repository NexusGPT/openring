# J1 pads: number and net on the board
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); f = b.FindFootprintByReference("J1")
pads = [(p.GetNumber(), p.GetNetname()) for p in f.Pads()]
print("J1 pads", len(pads)); print(pads)
print("pads with no net:", [n for n, net in pads if not net])
