#!/bin/bash
# usage: run_kipy.sh script.py [args]  -- runs a script with KiCad's own Python 3.9 (has the pcbnew module)
K=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9
PYTHONPATH=$K/lib/python3.9/site-packages exec $K/bin/python3 "$@"
