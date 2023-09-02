# Copyright 2023 iiPython & DmmD GM

# Modules
from typing import Any, List
from types import FunctionType

from .keypress import readchar

# Dataclasses
class Raw:
    pass

class Converted:
    pass

class Spacer(object):
    def __init__(self, text: str) -> None:
        self.text = text

# Main builtins handler
class EnglishBuiltins(object):
    def __init__(self) -> None:
        self.builtins = {}

    def builtin(self, takes_args: List[Converted | Spacer | Raw]) -> FunctionType:
        def internal(func: FunctionType):
            def callback_processor(this, *args) -> Any:
                new_args = []
                for index, arg_type in enumerate(takes_args):
                    item = args[index] if len(args) - 1 >= index else (None, None)
                    if arg_type == Raw:
                        new_args.append(item[1])

                    elif (arg_type == Converted) and (item is not None):
                        new_args.append(item[0])

                    elif (type(arg_type) == Spacer) and \
                         (arg_type.text != item[1]):
                        exit("english: improper transition word in sentence.")

                return func(this, *new_args)

            if not takes_args:
                def raw_processor(this, *args) -> None:
                    return func(this, *[a[0] for a in args])

                callback_processor = raw_processor  # noqa: F811

            self.builtins[func.__name__.split("_")[1]] = callback_processor

        return internal

# Pre-initialize class
builtins = EnglishBuiltins()

# Start exporting builtins
@builtins.builtin([Converted, Spacer("of"), Converted, Spacer("to"), Converted])
def builtin_set(self, key: str | int, object: dict | list, value: Any) -> None:
    if isinstance(object, list):
        if isinstance(key, str):
            raise IndexError("arrays do not support object-like keys.")

        # Ensure this list is padded enough for you to
        # index with whatever key we were given
        object += [None] * ((key or 1) - len(object))

    object[key] = value

@builtins.builtin([Converted, Spacer("from"), Converted, Spacer("as"), Raw])
def builtin_get(self, key: str | int, object: dict | list, variable: str) -> None:
    self.variables[variable] = object[key]

@builtins.builtin([])
def builtin_print(self, *args) -> None:
    print(*args)

@builtins.builtin([Converted, Spacer("as"), Raw])
def builtin_input(self, prompt: str, variable: str) -> None:
    self.variables[variable] = input(prompt)

@builtins.builtin([Spacer("as"), Raw])
def builtin_readkey(self, variable: str) -> None:
    key = readchar()
    self.variables[variable] = key if isinstance(key, str) else ""

@builtins.builtin([Raw, Raw])
def builtin_jump(self, location: str, name: str) -> None:
    match location:
        case "back":
            last_stack = self.stack.pop()
            if last_stack[1] == "epilogue":
                exit(0)

            self.current_line = last_stack[0] - 1

        case "last":
            self.current_line = self.chapters[self.stack[-1][1]] - 1
        
        case "to":
            self.stack.append((self.current_line + 1, name))
            chapter_line = self.chapters.get(name)
            if chapter_line is None:
                if name == "epilogue":
                    exit(0)

                raise ValueError(
                    "cannot jump to a non-existant chapter.")

            self.current_line = chapter_line - 1

        case _:
            raise ValueError("you're trying to jump *where*?")
