"""Find the mechanical pages of the saved microphone datasheet copies and render them to PNG.
Usage: python -I render_pages.py <out_dir> <pdf> [<pdf> ...]
Prints, per PDF, the pages whose text holds a port or pin table keyword, and writes <out_dir>/<stem>-p<N>.png at 200 dpi."""
import sys
from pathlib import Path
import fitz

KEYS = ("Acoustic Port", "Pin Name", "Pin #", "Sound hole", "sound hole", "Dimension", "PIN", "Port")


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for f in sys.argv[2:]:
        d = fitz.open(f)
        stem = Path(f).stem
        for i, p in enumerate(d):
            t = p.get_text()
            hits = [k for k in KEYS if k in t]
            if hits:
                png = out / f"{stem}-p{i + 1}.png"
                p.get_pixmap(dpi=200).save(str(png))
                print(f"{f} page {i + 1} of {len(d)}: keys {hits} -> {png}")


if __name__ == "__main__":
    main()
