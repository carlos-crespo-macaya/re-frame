"""Backend test runner site customisations.

This mirrors the root-level *sitecustomize.py* so that the module is found when
the test suite is executed from the ``backend`` directory (which is the
default working directory defined in *pyproject.toml*).
"""

# Re-export everything from the root implementation if it exists.  We import
# it using a relative import so that the logic is defined in a single place.

from importlib import import_module as _im

# The sibling module lives one directory up – add parent to ``sys.path`` so the
# original implementation can be located regardless of the cwd.
import sys
from pathlib import Path

parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

_im("sitecustomize")  # noqa: F401 – side-effects only

