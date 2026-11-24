"""Hand over the finished front page for news-image-20261123.

The graded program has a single job: take the ``entry.png`` that is
already committed next to this file in the repository and put a
byte-identical copy at ``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output``
when that variable is not set). It does not draw anything, does not
rebuild anything, and never writes into the repository directory, so
it runs fine when the repository is mounted read-only.
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
