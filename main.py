"""Ship the finished front page for news-image-20261123.

This program does one thing and nothing else: it takes the
``entry.png`` that is already committed next to this file and puts an
exact copy of it at ``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output`` if
the variable is not set). It does not draw anything, does not rebuild
anything, and does not write into the repository directory, so it
still works when the repository is mounted read-only.
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
    print(f"delivered {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
