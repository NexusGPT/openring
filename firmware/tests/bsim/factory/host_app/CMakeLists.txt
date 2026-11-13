cmake_minimum_required(VERSION 3.20.0)

# The scanner of the ship beacon test: a stand-in for the jig that listens to the ring's advertising (a passive scan, no
# connection). Driven by a script of times in main.c.
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_factory_bsim_scanner)

target_sources(app PRIVATE src/main.c)
