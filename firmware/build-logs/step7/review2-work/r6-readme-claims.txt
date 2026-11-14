70:CELL (Nordic's 20 mAh sample, a stand-in); a copy of the netlist, which `tools/remote.sh` compares with
80:What is unproven: everything that needs a ring. It compiles and its pins match the netlist; no ring has run it. The
81:power part's real file compiles and is on (`CONFIG_RING_POWER_REAL=y`), with a cell model that is NOT THE RING'S CELL;
83:SDK's debug key ("for debug use only and is not secure"): NOT FOR SHIPPING; the production key is made at the factory
100:| `modules/ring_store/`, `ring_audio/`, `ring_xfer/`, `ring_power/`, `ring_motor/`, `ring_sys/`, `ring_factory/` | step 6: storage, microphones, USB transfer, power, motor, system (update, crash, watchdog, saved time), factory tests; each has a pure part and a thin part; the real driver files (`*_hw_real.c`) build for the development kit (most of them empty there: no node) and for the ring board (step 7, real code), and are not proven |
--- kit sizes evidence search (empty / text 0) in f1-full1 and step6 logs
29314:ring-drivers: rau_hw_real.c.obj text 536 bytes: real code
29328:ring-drivers: rfa_hw_real.c.obj text 154 bytes: real code
29332:ring-drivers: rmo_hw_real.c.obj text 108 bytes: real code
29335:ring-drivers: rpw_hw_real.c.obj text 6840 bytes: real code
29387:ring-drivers: rst_hw_real.c.obj text 326 bytes: real code
29398:ring-drivers: rsy_hw_real.c.obj text 796 bytes: real code
29419:ring-drivers: rxf_hw_real.c.obj text 848 bytes: real code
firmware/build-logs/step7/s7-stages1.console
firmware/build-logs/step7/20261113-213944-s7-stages1.log
firmware/build-logs/step7/20261113-214232-s7-full1.log
firmware/build-logs/step7/lead-full5.console
firmware/build-logs/step7/s7-full1.console
firmware/build-logs/step7/fix1/f1-stages1.console
firmware/build-logs/step7/fix1/20261114-000621-f1-stages1.log
firmware/build-logs/step7/20261113-234842-lead-full5.log
firmware/build-logs/step7/review2-work/r6-readme-claims.txt
firmware/build-logs/step7/fix1/20261114-001111-f1-full1.log
