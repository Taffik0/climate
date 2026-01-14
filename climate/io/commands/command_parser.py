import inspect
from typing import TYPE_CHECKING

from .command import Flag, WordFlag, Command
from climate.utils.safe_func import safe_call


class CommandParser:
    def __init__(self):
        pass

    def parse_flags(self, command: Command, text: str):
        blocs = text.split()
        flags = self.find_flag(blocs)
        flags_dict = {f.name: f.kwarg for f in command.flags}
        args_dict = {}
        for name, value in flags.items():
            # вернёт None, если флаг не зарегистрирован
            kwarg = flags_dict.get(name)
            if kwarg is not None:
                args_dict[kwarg] = value
            else:
                print(f"Неизвестный флаг: {name}")
        return args_dict

    def find_flag(self, blocs: list[str]):
        result = {}
        index = 0

        while index < len(blocs):
            bloc = blocs[index]

            # --- длинный флаг ---
            if bloc.startswith("--"):
                name, value, consumed = self._parse_long_flag(blocs, index)
                result[name] = value
                index += consumed
                continue

            # короткие флаги
            if bloc.startswith("-") and not bloc.startswith("--"):
                flags = bloc[1:]

                # === 1) Групповые флаги: -cx ===
                if len(flags) > 1:
                    for f in flags[:-1]:
                        result[f] = None

                    last = flags[-1]
                    value = None
                    if index + 1 < len(blocs) and not blocs[index + 1].startswith("-"):
                        value = blocs[index + 1]
                        index += 1

                    result[last] = value
                    index += 1
                    continue

                # === 2) Одиночный флаг: -b ===
                if len(flags) == 1:
                    name = flags
                    value = None

                    # аргумент?
                    if index + 1 < len(blocs) and not blocs[index + 1].startswith("-"):
                        value = blocs[index + 1]
                        index += 1

                    result[name] = value
                    index += 1
                    continue

            index += 1

        return result

    def _parse_long_flag(self, blocs: list[str], index: int):
        """
        Разбирает длинный флаг --name [value]
        Возвращает: (name, value, сколько токенов съел)
        """
        bloc = blocs[index]
        name = bloc[2:]
        value = None
        consumed = 1

        if index + 1 < len(blocs) and not blocs[index + 1].startswith("-"):
            value = blocs[index + 1]
            consumed += 1

        return name, value, consumed

    def extract_command(self, text: str):
        blocs = text.split()
        if not blocs:
            return None, [], ""

        command = blocs[0]
        args = []
        index = 1

        # собираем позиционные аргументы до первого слова, начинающегося с "-"
        while index < len(blocs) and not blocs[index].startswith("-"):
            args.append(blocs[index])
            index += 1

        return command, args

    def parse_command(self, commands: list[Command], text: str):
        command_name, positional_args = self.extract_command(text)
        command = {c.name: c for c in commands}[command_name]
        kwargs = self.parse_flags(command, text)
        return command, positional_args, kwargs

    def execute_command(self, command: Command, args, kwargs):
        safe_call(command.method, args, kwargs)


def _brbr(count: int = 1):
    if count:
        for i in range(count):
            print("br br br")


if __name__ == "__main__":
    commands = [Command(_brbr, "start", [Flag("c", "count")])]
    command_parser = CommandParser()
    command, positional_args, kwargs = command_parser.parse_command(
        commands, "start -c 20")
    print(command, positional_args, kwargs)
    command_parser.execute_command(command, positional_args, kwargs)
