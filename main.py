#!/usr/bin/env python3
"""Entry point: copy the pre-built entry.png to the output dir.

This program does NOT draw anything. It only copies the committed
entry.png into MAKEFUN_OUTPUT_DIR, so it runs cleanly even when the
repository is mounted read-only.
"""
from __future__ import annotations

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    print("delivered %s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
