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

# Helper functions
def perform_if_statement(self, content: List[str]) -> Tuple[bool, str]:
    parsed, in_condition, payload = [], False, ""
    for item in content:
        if payload in [
            "is equal to",
            "is not equal to",
            "is less than",
            "is greater than"
        ]:
            in_condition = False
            parsed.append(payload)
            payload = ""

        if item == "is":
            parsed.append(payload)
            payload = item
            in_condition = True

        elif item == "then":
            parsed.append(payload)
            payload = ""

        else:
            payload += (" " + item if (payload or in_condition) else item)

    data = parsed + [payload]
    value1, value2, cond = self.eval_expr(data[0]), self.eval_expr(data[2]), data[1]
    return ((value1 == value2) and (cond == "is equal to")) or \
            ((value1 != value2) and (cond == "is not equal to")) or \
            ((value1 < value2) and (cond == "is less than")) or \
            ((value1 > value2) and (cond == "is greater than")), data[3]

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

@builtins.builtin("if")
def builtin_if(self, *content) -> None:
    resp, expr = perform_if_statement(self, [a.raw for a in content])
    if resp:
        self.exec_line(self.split_line(expr))

    self.comp_stack.append(resp)

@builtins.builtin("otherwise")
def builtin_otherwise(self, *content) -> None:
    if (self.lines[self.line - 1].split(" ")[0] not in ["if", "otherwise"]) or \
        not self.comp_stack:
        raise RuntimeError("otherwise must be used in conjunction with an if branch.")

    elif content[0] != "if" and self.comp_stack[-1] is False:
        self.exec_line([a.raw for a in content])

    self.comp_stack.pop()
    if content[1] == "if":
        builtin_if(self, *content[1:])

@builtins.builtin("get", [(1, "from"), (3, "as")])
def builtin_get(self, key: str | int, object: dict | list, variable: str) -> None:
    self.variables[variable.raw] = object.obj[key.obj]

@builtins.builtin("set", [(1, "of"), (3, "to")])
def builtin_set(self, key: str | int, object: str, value: Any) -> None:
    key, obj = key.obj, self.variables[object.raw]
    if isinstance(obj, list):
        obj += [None] * (key - (len(obj) - 1))

    obj[key] = value.obj

# Post-init
builtins = builtins.builtins  # Fetch the mapping only
