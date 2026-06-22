"""Make the in-tree ``mplayer_server`` package importable without installing.

Lets ``python -m pytest`` work from a fresh checkout. (Installing with
``pip install -e .[dev]`` also works and makes this redundant.)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
