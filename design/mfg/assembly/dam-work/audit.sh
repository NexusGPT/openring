#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Final audit of dam-material-notes.md: every bracketed citation must name a quote ID in quotes.tsv,
# and its page and line must match the saved verify log (quotes-verify.log). Bare "p.N l.L" citations are
# printed with the saved line of every sheet at that line, for reading.
O="$REPO_ROOT/design/mfg/assembly/dam-work"
D="$REPO_ROOT/design/datasheets"
NOTES="$O/dam-material-notes.md"
QT="$O/quotes.tsv"
LOG="$O/quotes-verify.log"
checked=0; bad=0

echo "== 1. bracketed citations p.N l.L [ID]"
while read -r cite; do
  pg=$(echo "$cite" | sed -E 's/^p\.([0-9]+) l\.([0-9]+) \[([^]]+)\]$/\1/')
  ln=$(echo "$cite" | sed -E 's/^p\.([0-9]+) l\.([0-9]+) \[([^]]+)\]$/\2/')
  id=$(echo "$cite" | sed -E 's/^p\.([0-9]+) l\.([0-9]+) \[([^]]+)\]$/\3/')
  checked=$((checked+1))
  row=$(awk -F'\t' -v I="$id" '$1==I {print; exit}' "$QT")
  if [ -z "$row" ]; then echo "BAD no such ID: $id ($cite)"; bad=$((bad+1)); continue; fi
  file=$(echo "$row" | cut -f2); qline=$(echo "$row" | cut -f3)
  logrow=$(grep -F "| $id |" "$LOG")
  lpage=$(echo "$logrow" | sed -E 's/.*\| page ([0-9]+) \|.*/\1/')
  if [ "$qline" != "$ln" ] || [ "$lpage" != "$pg" ]; then
    echo "BAD $cite: quote table says line $qline page $lpage ($file)"; bad=$((bad+1)); continue
  fi
  echo "ok  $cite -> $file line $qline page $lpage"
done < <(grep -o -E 'p\.[0-9]+ l\.[0-9]+ \[[^]]+\]' "$NOTES")

echo "== 2. every [ID] mention in the notes exists in quotes.tsv"
while read -r id; do
  if ! awk -F'\t' -v I="$id" '$1==I {f=1} END {exit !f}' "$QT"; then echo "BAD unknown ID [$id]"; bad=$((bad+1)); fi
done < <(grep -o -E '\[[A-Za-z0-9][^] ]*\]' "$NOTES" | tr -d '[]' | grep -v '^[0-9]*$' | sort -u)

echo "== 3. bare citations p.N l.L (not in brackets): saved line in each sheet at that line"
grep -o -E 'p\.[0-9]+ l\.[0-9]+[-0-9]*' "$NOTES" | grep -v '\[' | sort -u | while read -r b; do
  ln=$(echo "$b" | sed -E 's/^p\.[0-9]+ l\.([0-9]+).*/\1/')
  for f in dam_dymax_9014.txt dam_dymax_9422-sc.txt dam_henkel-loctite_si-5240.txt dam_panacol_vitralit-ud8060f.txt dam_henkel-loctite_uv300x.txt; do
    echo "$b | $f:$ln | $(sed -n "${ln}p" "$D/$f" | sed 's/  */ /g' | cut -c1-120)"
  done
done

echo "== 4. quote check (from the verify log)"
tail -n 1 "$LOG"
echo "bracketed citations checked: $checked, problems: $bad"
