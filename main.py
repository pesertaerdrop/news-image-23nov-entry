"""Deliver the committed front page to the grader's output folder.

This is the graded program. It does one thing: copy the entry image
that already lives in this repo into MAKEFUN_OUTPUT_DIR. It never
builds anything, never imports the builder, and never writes into
this repo, so it runs fine even when the repo is mounted read-only.
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
    print("delivered", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
