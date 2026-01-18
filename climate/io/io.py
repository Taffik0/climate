import asyncio
import os

import threading
import time
from typing import Any, TYPE_CHECKING, Optional

from .template_string import TemplateString
from .console_manager import ConsoleManager
from .buffer import Buffer
from .commands.command_parser_v2 import CommandParserV2
from .commands.command import Command, ParsedCommand

if TYPE_CHECKING:
    from climate.page.page import Page
    from climate.app import App


class IO:
    def __init__(self, incorrect_input_error: str = "incorrect input",
                 page: Optional["Page"] = None,
                 app: Optional["App"] = None,
                 buffer: Optional["Buffer"] = None):
        self.out_prefix = ""
        self.incorrect_input_error = incorrect_input_error

        self.global_commands: list["Command"] = []
        self.global_commands_prefix = "/"

        self.scrollable: bool = False

        if app:
            self.app = app
            self.console_manager: "ConsoleManager" = app.console_manager
        else:
            self.console_manager: "ConsoleManager" = ConsoleManager()

        self.console_manager.start()
        if page:
            self.page = page
            self.app = page.app

            self.out_prefix = page.out_prefix

            self.global_commands += page.commands
            self.global_commands_prefix = page.command_prefix
            self.command_parser = CommandParserV2()

            self.scrollable = page.scrollable

        self.buffer = Buffer()
        if buffer:
            self.buffer = buffer
        if self.scrollable:
            self.console_manager.subscribe_on_scroll(self.scroll)

    def _input(self, prompt=">>> "):
        """
        Синхронно ждём, пока пользователь введёт строку в асинхронном ACM
        """
        # future вернётся, когда user нажмёт Enter
        future = asyncio.run_coroutine_threadsafe(
            self.console_manager.input_async(prompt),
            self.console_manager.loop  # loop должен быть запущен
        )
        return future.result()

    def input(self, input_prefix: str, permitted_symbols: str | None = None, check_global_commands: bool = True):
        while True:
            input_text = self._input(prompt=f"{input_prefix}")

            if check_global_commands:
                if self.check_command([], input_text, run_fuc=True):
                    continue

            if permitted_symbols and not all(symbol in permitted_symbols for symbol in input_text):
                continue

            return input_text

    def submit(self, query: str = ""):
        return self.input(f"{query} Y/n ") == "Y"

    def number_choice(self, query_list: list, query: str = "",
                      out_temp: TemplateString | None = None) -> tuple[int, Any]:
        if query != "":
            query += " "
        for i, item in enumerate(query_list):
            if out_temp:
                self.print(out_temp.string(args={"num": i, "item": item}))
            else:
                self.print(f"({i}) {item}", end=" ")
        self.print("", end="\n")
        index = -1
        while not (index >= 0 and index < len(query_list)):
            index = int(self.input(f"{query}"))
            if not (index >= 0 and index < len(query_list)):
                self.print(f"incorrect index {index} max {len(query_list)-1}")
        return index, query_list[index]

    def string_choice(self, query_list: list[str], query: str | TemplateString = "",
                      out_temp: TemplateString | None = None) -> tuple[int, str]:
        if query != "" and type(query) is str:
            query += " "
        first_symbols = []
        for txt in query_list:
            if out_temp:
                self.print(out_temp.string(
                    args={"first": txt[0].upper(), "word": txt[1:]}), end=" ")
            else:
                self.print(f"({txt[0].upper()}){txt[1:]}", end=" ")
            first_symbols.append(txt[0].lower())
        self.print("")
        choice = ""
        while not (choice.lower() in first_symbols):
            choice = self.input(f"{str(query)}").lower()
        return first_symbols.index(choice), query_list[first_symbols.index(choice)]

    def print(self, text: str | TemplateString, end: str = "\n"):
        if isinstance(text, str):
            self.buffer.add_out_text(text + end)
        else:
            self.buffer.add_out_text(text)
            self.buffer.add_out_text(end)
        self._update_buffer()

    def write(self, text: str | TemplateString, end: str = ""):
        if isinstance(text, str) and isinstance(self.buffer.out_text[-1], str):
            self.buffer.out_text[-1] += text + end
        self.print(text, end=end)
        self._update_buffer()

    def _update_buffer(self):
        self.console_manager.draw_buffer(self.buffer)

    def say(self, text: str | Any, name: str, out_temp: TemplateString | None = None):
        if out_temp:
            self.print(out_temp.string(
                args={"name": str(name), "text": str(text)}))
        else:
            self.print(f"[{name}] {text}")

    def clear(self, text: bool = True, bottom: bool = True, top: bool = True):
        if text:
            self.buffer.out_text.clear()
        if bottom:
            self.buffer.bottom_lines.clear()
        if top:
            self.buffer.top_lines.clear()

    def check_command(self, commands: list["Command"],
                      input: str,
                      global_commands: bool = True,
                      run_fuc: bool = False) -> ParsedCommand | None:
        parsed_command = self.command_parser.parse_commands(commands, input)

        if input[:len(self.global_commands_prefix)] == self.global_commands_prefix and global_commands:
            parsed_command = self.command_parser.parse_commands(
                self.global_commands, input[len(self.global_commands_prefix):])

        if parsed_command and run_fuc:
            parsed_command.call()
        return parsed_command

    def input_command(self, commands: list["Command"], input_prefix: str,  run_command: bool = True) -> Optional["ParsedCommand"]:
        input_command = self._input(prompt=f"{input_prefix}")
        return self.check_command(commands, input_command, run_fuc=run_command)

    def scroll(self, movement: int) -> None:
        self.buffer.offset = max(self.buffer.offset + movement, 0)
        self._update_buffer()

    def exit(self):
        self.console_manager.unsubscribe_on_scroll(func=self.scroll)

    def restart(self):
        if self.scrollable:
            self.console_manager.subscribe_on_scroll(self.scroll)


def start_console(cm: ConsoleManager):
    asyncio.set_event_loop(cm.loop)
    cm.loop.run_until_complete(cm.run_app())


if __name__ == "__main__":
    io = IO()
    time.sleep(0.1)
    io.print("ffffffff")
    io.print("ffffffff")
    io.print("ffffffff")
    text = ""
    while text != "0":
        text = io.input(">>>  ")
        print("h")
        io.print(text)
