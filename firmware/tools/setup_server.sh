#!/bin/bash
# setup_server.sh: one-time setup of the ring firmware workspace on the build
# server. Safe to run again: each step skips what is already done.
#
# Usage, from the Mac:  sh firmware/tools/remote.sh -H setup "bash tools/setup_server.sh"
# Usage, on the server: cd /root/ring-os/src && bash tools/setup_server.sh
#
# Steps:
#   1. pull ghcr.io/nrfconnect/sdk-nrf-toolchain:v3.4.2 (Nordic's image for
#      sdk-nrf tag v3.4.2; sdk-nrf .github/workflows/docker.yml line 58-62
#      tags the image with the git tag name)
#   2. build ring-os-toolchain:v3.4.2 from tools/Dockerfile (adds make; the
#      32-bit C library for the bsim boards)
#   3. west workspace /root/ring-os/ws (in the container: /ws, with this folder
#      mounted at /ws/firmware): west init -l, then west update --narrow
#      with shallow clones
#   4. build BabbleSim in /ws/tools/bsim with make everything
# Each heavy step first checks that at least 25 GB are free on /.

set -u
R=/root/ring-os
BASE_IMAGE=ghcr.io/nrfconnect/sdk-nrf-toolchain:v3.4.2
IMAGE=ring-os-toolchain:v3.4.2
SRC=$(cd "$(dirname "$0")/.." && pwd)

step() { echo "=== setup: $* ($(date -u '+%Y-%m-%dT%H:%M:%SZ'))"; }

check_disk() {
	local free_gb
	free_gb=$(df -BG --output=avail / | tail -1 | tr -dc '0-9')
	echo "free on /: ${free_gb} GB"
	if [ "$free_gb" -lt 25 ]; then
		echo "setup: STOP, less than 25 GB free on /"
		exit 1
	fi
}

in_container() {
	nice -n 19 docker run --rm --name "ring-os-setup-$$" --cpus 8 \
		-v "$R/ws:/ws" -v "$SRC:/ws/firmware" -w /ws \
		-e BSIM_OUT_PATH=/ws/tools/bsim -e BSIM_COMPONENTS_PATH=/ws/tools/bsim/components \
		"$IMAGE" "nice -n 19 bash -c '$1'"
}

mkdir -p "$R/ws" "$R/logs" "$R/runs"

step "1 pull $BASE_IMAGE"
check_disk
nice -n 19 docker pull "$BASE_IMAGE" || exit 1

step "2 build $IMAGE from $SRC/tools/Dockerfile"
check_disk
nice -n 19 docker build -t "$IMAGE" -f "$SRC/tools/Dockerfile" "$SRC/tools" || exit 1

step "3 west workspace in $R/ws"
check_disk
if [ ! -d "$R/ws/.west" ]; then
	in_container "west init -l /ws/firmware" || exit 1
fi
in_container "west update --narrow -o=--depth=1 && west list -f \"{name} {revision} {path}\"" || exit 1
du -sh "$R/ws"

step "4 BabbleSim in $R/ws/tools/bsim"
check_disk
in_container "cd /ws/tools/bsim && make everything -j 8" || exit 1
ls "$R/ws/tools/bsim/bin" | head -20

step "done"
df -h /
du -sh "$R"
docker image ls --format "{{.Repository}}:{{.Tag}} {{.Size}}" | grep -E "ring-os|sdk-nrf-toolchain"
