import asyncio
import os

import threading
import time
from typing import Any, TYPE_CHECKING, Optional

from .template_string import TemplateString
from .console_manager import ConsoleManager
from .buffer import Buffer

if TYPE_CHECKING:
    from climate.page.page import Page
    from climate.app import App


class IO:
    def __init__(self, incorrect_input_error: str = "incorrect input",
                 page: Optional["Page"] = None,
                 app: Optional["App"] = None,
                 buffer: Optional["Buffer"] = None):
        self.out_prefix = ""

        if app:
            self.app = app
            self.console_manager: "ConsoleManager" = app.console_manager
        else:
            self.console_manager: "ConsoleManager" = ConsoleManager()
        if page:
            self.page = page
            self.app = page.app

            self.out_prefix = page.out_prefix

        self.buffer = Buffer()
        if buffer:
            self.buffer = buffer

        self.incorrect_input_error = incorrect_input_error

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

    def input(self, input_prefix: str, permitted_symbols: str | None = None):
        if permitted_symbols:
            input_text = ""
            is_valid = False
            while not is_valid:
                input_text = self._input(
                    prompt=f"{input_prefix}")
                is_valid = True
                for symbol in input_text:
                    is_valid = is_valid and symbol in permitted_symbols
            return input_text
        else:
            return self._input(prompt=f"{input_prefix}")

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

    def print(self, text: str | Any, end="\n"):
        self.buffer.out_text += text + end
        self._update_buffer()

    def write(self, text: str | Any, end=""):
        self.buffer.out_text += text + end
        self._update_buffer()

    def _update_buffer(self):
        self.console_manager.draw_buffer(self.buffer)

    def say(self, text: str | Any, name: str, out_temp: TemplateString | None = None):
        if out_temp:
            self.print(out_temp.string(
                args={"name": str(name), "text": str(text)}))
        else:
            self.print(f"[{name}] {text}")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')


def start_console(cm: ConsoleManager):
    asyncio.set_event_loop(cm.loop)
    cm.loop.run_until_complete(cm.run_app())


if __name__ == "__main__":
    io = IO()
    cm = io.console_manager
    threading.Thread(
        target=start_console,
        args=(cm,),
        daemon=True
    ).start()
    time.sleep(0.1)
    io.print("ffffffff")
    text = io.input("br br", permitted_symbols="1234567890")
    io.print(text)
