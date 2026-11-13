#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
cd $REPO_ROOT/design/mech/thin
printf "%s\n" broken_led broken_height default us7 us13 us8 us10 us11 us12 us9 | xargs -P 4 -I{} out/v7/run_one.sh {}
date > out/v7/run_all.done
