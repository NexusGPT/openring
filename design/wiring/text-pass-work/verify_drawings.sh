#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
D=$REPO_ROOT/design/mfg/drawings
for pair in "radio-corner.svg:EP30Med" "radio-corner.svg:RC1" "flex-tail-thumb-footstiffener-us9.svg:Polyimide, 0.10" "flex-tail-thumb.svg:Polyimide, 2 copper" "joystick-stiffener.svg:Polyimide, 0.10" "main-board.svg:4 copper layers" "main-board.svg:no notch" "ring-assembly.svg:2.1 x 0.6" "body.svg:inside model v9" "body-us10.svg:body-us10.step in design/mfg/parts/body/" "flex-tail-thumb-footstiffener-us9.svg:flex-tail-thumb-footstiffener-us9.step in design/mfg/parts/flex-tail-thumb/"; do
  f=${pair%%:*}; s=${pair#*:}
  n=$(grep -c -F "$s" "$D/$f")
  echo "$f | $s | lines $n"
done
echo "svg sheets: $(ls $D | grep -c '\.svg$')"
echo "pdf sheets: $(ls $D | grep -c '\.pdf$')"
echo "stale v7 title in drawings: $(grep -l -F 'inside model v7' $D/*.svg | wc -l)"
