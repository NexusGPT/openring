"""Runs one ngspice deck through KiCad's own libngspice (no ngspice executable is shipped).
Usage: python ngrun.py deck.cir out.txt   -> writes the output of the deck's .control block to out.txt
"""
import ctypes, sys, os
LIB = "/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.dylib"

SendChar = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
SendStat = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
ControlledExit = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
SendData = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)
SendInit = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p)
BGThread = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)

def run(deck, out):
    lib = ctypes.CDLL(LIB)
    lines = []
    def sc(s, i, u):
        lines.append(s.decode(errors="replace")); return 0
    def ss(s, i, u): return 0
    def ce(a, b, c, d, e): return 0
    def sd(a, b, c, d): return 0
    def si(a, b, c): return 0
    def bg(a, b, c): return 0
    cbs = (SendChar(sc), SendStat(ss), ControlledExit(ce), SendData(sd), SendInit(si), BGThread(bg))
    lib.ngSpice_Init.argtypes = [SendChar, SendStat, ControlledExit, SendData, SendInit, BGThread, ctypes.c_void_p]
    lib.ngSpice_Init(*cbs, None)
    lib.ngSpice_Command.argtypes = [ctypes.c_char_p]
    d = os.path.dirname(os.path.abspath(deck))
    beh = os.environ.get("NGBEHAVIOR")
    if beh:
        lib.ngSpice_Command(("set ngbehavior=" + beh).encode())
    lib.ngSpice_Command(("source " + os.path.abspath(deck)).encode())
    lib.ngSpice_Command(b"quit")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    return lines

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
