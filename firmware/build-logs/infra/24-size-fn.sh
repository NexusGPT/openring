size_report() {
	# Each table is followed by "Generating files from <build>/<image>/zephyr/zephyr.elf",
	# which names the image the table belongs to.
	awk '/Memory region[ \t]+Used Size/ {p=1; buf=$0 "\n"; next}
	     p && /^[ \t]*[A-Za-z0-9_]+:[ \t]+[0-9]+/ {buf=buf $0 "\n"; next}
	     p && /Generating files from .*zephyr\.elf/ {n=split($4, a, "/"); img=(n>=3 ? a[n-2] : $4);
	        printf "image %s (%s)\n%s", img, $4, buf; p=0; next}
	     p {printf "image unknown\n%s", buf; p=0}' "$1"
}
