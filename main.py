#!/usr/bin/env python3
"""Entry program for make.fun competition news-image-20261119,
"Sum up 19 November's world news in one image".

The picture (entry.png, drawn by build_image.py) sits beside this file
in the repository. The program's one job is to write it, byte for byte,
to the output directory as entry.png:

    /output/entry.png            in the grader's sandbox
    $MAKEFUN_OUTPUT_DIR/entry.png anywhere else

Standard library only, no network, deterministic: every run copies the
same bytes.
"""

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576  # the gate takes at most 1 MiB
MAX_SIDE = 1024        # and at most 1024 x 1024 pixels


def check_image(data: bytes) -> None:
    """Raise ValueError unless data is a whole PNG inside the gate limits."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")
    if len(data) > MAX_BYTES:
        raise ValueError(f"image is {len(data)} bytes, over the 1 MiB limit")
    # IHDR is the first chunk: 8-byte signature, 4 length, 'IHDR', then
    # width and height as big-endian uint32.
    if data[12:16] != b"IHDR":
        raise ValueError("first PNG chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"image is {width}x{height}, over the 1024x1024 limit")


def main() -> int:
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    if not src.is_file():
        print(f"error: {src} is missing from the repository", file=sys.stderr)
        return 1

    try:
        check_image(src.read_bytes())
    except ValueError as exc:
        print(f"error: entry.png fails the gate: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)

    data = dst.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {dst} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
