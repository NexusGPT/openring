# Smoke test of the build workspace: proves twister finds, builds and runs a
# ztest suite on native_sim and on the simulated ring chip.

cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ring_smoke)

target_sources(app PRIVATE src/main.c)
