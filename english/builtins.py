# Copyright 2023 iiPython & DmmD GM

# Modules
from types import FunctionType
from typing import Any, List, Tuple

from dataclasses import dataclass

# Dataclass
@dataclass
class Argument:
    raw: str
    obj: Any

# Master class
class Builtins(object):
    def __init__(self) -> None:
        self.builtins = {}

    def builtin(
        self,
        name: str,
        spacer_args: List[Tuple[int, str]] = []
    ) -> None:
        def internal(fn: FunctionType) -> Any:
            def callback_processor(this, *args) -> Any:
                for spacer in spacer_args:
                    if args[spacer[0]].raw != spacer[1]:
                        raise ValueError("Invalid transition word inside line.")
                    
                return fn(this, *args)

            if not spacer_args:
                callback_processor = fn  # noqa: F811
            
            self.builtins[name] = callback_processor

        return internal

# Pre-init
builtins = Builtins()

# Main builtins
@builtins.builtin("print")
def builtin_print(self, *args) -> None:
    print(*[a.obj for a in args])

# Post-init
builtins = builtins.builtins  # Fetch the mapping only
