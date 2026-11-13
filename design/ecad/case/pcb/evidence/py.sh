#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
exec $REPO_ROOT/design/.venv/bin/python -W ignore -I "$@"
