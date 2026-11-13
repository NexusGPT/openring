# ring-os-toolchain: Nordic's nRF Connect SDK v3.4.2 toolchain image plus
# what the simulated chip boards need.
# Built by tools/setup_server.sh as ring-os-toolchain:v3.4.2.
#
# - make: BabbleSim is built with "make everything" (the base image has no make).
# - gcc-multilib, libc6-dev-i386: the bsim boards need the host 32-bit C library
#   (nrf52_bsim.rst line 62-63). The base image already has them; listing them
#   here keeps the image correct if a later base image drops them.

FROM ghcr.io/nrfconnect/sdk-nrf-toolchain:v3.4.2

RUN apt-get update \
 && apt-get install -y --no-install-recommends make gcc-multilib g++-multilib libc6-dev-i386 \
 && apt-get clean
