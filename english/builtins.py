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
                spacer_indexes = []
                for spacer in spacer_args:
                    if args[spacer[0]].raw != spacer[1]:
                        raise ValueError("Invalid transition word inside line.")

                    spacer_indexes.append(spacer[0])
 
                return fn(
                    this,
                    *[a for i, a in enumerate(args) if i not in spacer_indexes]
                )

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

@builtins.builtin("jump")
def builtin_jump(self, jump_type: str, location: str = None) -> None:
    if jump_type.raw == "back":
        last_stack = self.stack.pop()
        if last_stack[1] == "epilogue":
            exit(0)

        self.line = last_stack[0] - 1

    elif jump_type.raw == "last":
        self.line = self.chapters[self.stack[-1][1]] - 1

    elif jump_type.raw == "to":
        self.stack.append((self.line + 1, location.obj))
        chapter_line = self.chapters.get(location.obj)
        if chapter_line is None:
            if location.obj == "epilogue":
                exit(0)

            raise ValueError("cannot jump to a non-existant chapter.")

        self.line = chapter_line - 1

    else:
        raise ValueError("you're trying to jump *where*?")

# Post-init
builtins = builtins.builtins  # Fetch the mapping only
