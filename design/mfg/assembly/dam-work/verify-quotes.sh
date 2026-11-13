#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Checks each quote in quotes.tsv: grep -n -F must find it on the cited line of the saved text copy.
O="$REPO_ROOT/design/mfg/assembly/dam-work"
D="$REPO_ROOT/design/datasheets"
n=0; bad=0
while IFS=$'\t' read -r ID FILE LINE QUOTE; do
  [ "$ID" = "ID" ] && continue
  n=$((n+1))
  P="$D/$FILE"
  hit=$(grep -n -F -- "$QUOTE" "$P" | awk -F: -v L="$LINE" '$1==L {print $1; exit}')
  pg=$(( $(head -n "$LINE" "$P" | tr -cd '\f' | wc -c) + 1 ))
  if [ -n "$hit" ]; then st="FOUND"; else st="NOT_FOUND"; bad=$((bad+1)); fi
  txt=$(sed -n "${LINE}p" "$P" | sed 's/  */ /g' | cut -c1-140)
  echo "$st | $ID | $FILE:$LINE | page $pg | quote: [$QUOTE] | line: [$txt]"
done < "$O/quotes.tsv"
echo "quotes checked $n, not found $bad"
