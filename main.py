#!/usr/bin/env python3
"""Hand the finished front page to the grader.

The picture is already drawn and committed as entry.png. This script
does not draw anything: it only takes that file from this repository
and copies it into the directory the grader names with the
MAKEFUN_OUTPUT_DIR environment variable. Copying is all it does, so
it still runs when the repository is mounted read-only.
"""
from __future__ import annotations

import os
import shutil
import sys


def deliver() -> int:
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    picture = os.path.join(repo_dir, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(picture, target)
    print("delivered %s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
