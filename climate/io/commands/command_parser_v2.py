from typing import Any
from .command import Command, Flag, WordFlag, ParsedCommand


class CommandParserV2:
    def __init__(self) -> None:
        pass

    def parse_commands(self, commands: list[Command], command_line: str) -> ParsedCommand | None:
        parse_command_line = command_line.split()
        command_name_dict = {command.name: command for command in commands}
        current_command = command_name_dict.get(parse_command_line.pop(0))
        if not current_command:
            return None

        parameters, parse_command_line = self.parse_parameters(
            parse_command_line)
        parse_command_line = self.split_flags(parse_command_line)
        flags_arg_dict = self.parse_flag_args(
            parse_command_line, current_command.flags + current_command.word_flags)
        return ParsedCommand(current_command, parameters, flags_arg_dict)

    def split_flags(self, parse_command_line: list[str]) -> list[str]:
        result: list[str] = []
        for part in parse_command_line:
            if self.define_flag(part):
                result.extend(f"-{c}" for c in part[1:])
            else:
                result.append(part)
        return result

    def define_flag(self, line: str) -> bool:
        if len(line) >= 2:
            if line[0] == "-" and line[1] != "-":
                return True
        return False

    def define_word_flag(self, line: str) -> bool:
        if len(line) >= 3:
            if line[0] == "-" and line[1] == "-":
                return True
        return False

    def define_any_flag(self, line: str) -> bool:
        return self.define_flag(line) or self.define_word_flag(line)

    def get_flag_name(self, line: str) -> str | None:
        if self.define_flag(line):
            return line[1:]
        if self.define_word_flag(line):
            return line[2:]
        return None

    def parse_parameters(self, parse_command_line: list[str]) -> tuple[list[str], list[str]]:
        new_parse_command_line = parse_command_line.copy()
        parameters: list[str] = []
        for part in parse_command_line:
            if self.define_any_flag(part):
                return parameters, new_parse_command_line
            new_parse_command_line.pop(0)
            parameters.append(part)
        return parameters, new_parse_command_line

    def parse_flag_args(self, parse_command_line: list[str], flags: list[Flag]) -> dict[Flag, str | bool]:
        flags_arg: dict[Flag, str | bool] = {}
        flags_name_dict = {flag.name: flag for flag in flags}
        for index, part in enumerate(parse_command_line):
            if not self.define_any_flag(part):
                continue
            flag_name = self.get_flag_name(part)
            if not flag_name:
                continue
            flag = flags_name_dict.get(flag_name)
            if flag:
                if len(parse_command_line) > index+1 and not self.define_any_flag(parse_command_line[index+1]):
                    flags_arg[flag] = parse_command_line[index+1]
                else:
                    flags_arg[flag] = True
        return flags_arg
