from typing import Any

from climate.utils.safe_func import safe_call


class Flag:
    def __init__(self, name: str, kwarg: str | None):
        if len(name) > 1:
            raise
        self.name = name
        self.kwarg = kwarg


class WordFlag(Flag):
    def __init__(self, name: str, kwarg: str):
        self.name = name
        self.kwarg = kwarg


class Command:
    def __init__(self, method, name: str, flags: list[Flag], word_flags: list[WordFlag]):
        self.method = method
        self.name = name
        self.flags = flags
        self.word_flags = word_flags


class ParsedCommand:
    def __init__(self, command: Command, parameters: list[Any], parse_flags: dict[Flag, Any]):
        self.command = command
        self.parameters = parameters
        self.parse_flags = parse_flags

    def call(self):
        safe_call(self.command.method, self.parameters,
                  {flag.kwarg: self.parse_flags[flag] for flag in self.parse_flags})
