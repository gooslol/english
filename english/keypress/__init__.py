# Copyright 2023 iiPython

# Modules
import os
from . import keycodes as keys  # noqa: F401

if os.name == "nt":
    from .read_win import readchar  # noqa: F401

elif "nix" in os.name or os.name == "posix":
    from .read_linux import readchar  # noqa: F401
