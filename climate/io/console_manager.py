import asyncio
import threading
from typing import Callable
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer as TBuffer
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.filters import Condition

from .buffer import Buffer


class ConsoleManager:
    def __init__(self):
        self.loop = asyncio.new_event_loop()  # только создаём
        self._started = False

        self.input_buffer = TBuffer()
        self.output_lines = []
        self._prompt = ">>> "
        self._input_future = None

        self.scroll_subscribers = []

        def get_output_text():
            return "\n".join(self.output_lines)

        output_control = FormattedTextControl(get_output_text)
        output_window = Window(content=output_control, wrap_lines=True)

        input_control = BufferControl(
            buffer=self.input_buffer,
            input_processors=[BeforeInput(lambda: self._prompt)]
        )
        input_window = Window(content=input_control)

        layout = Layout(HSplit([output_window, input_window]))

        kb = KeyBindings()

        self.add_binds(kb)

        self.app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True,
            mouse_support=True,
        )

    def add_binds(self, kb: KeyBindings):
        @kb.add("enter")
        def accept(event):
            if self._input_future and not self._input_future.done():
                self._input_future.set_result(self.input_buffer.text)
            self.input_buffer.text = ""

        @kb.add("pageup")
        def scroll_up(event):
            self.call_scroll(1)

        @kb.add("pagedown")
        def scroll_down(event):
            self.call_scroll(-1)

    def get_mouse_handler(self):
        # это будет замыкание, видит self
        def handler(mouse_event):
            if mouse_event.event_type == MouseEventType.SCROLL_UP:
                self.call_scroll(1)
            elif mouse_event.event_type == MouseEventType.SCROLL_DOWN:
                self.call_scroll(-1)
            return None  # обязательно
        return handler

    def subscribe_on_scroll(self, func: Callable[[int], None]) -> int:
        self.scroll_subscribers.append(func)
        return self.scroll_subscribers.index(func)

    def unsubscribe_on_scroll(self, func: Callable[[int], None] | None = None, index: int | None = None):
        if func:
            self.scroll_subscribers.remove(func)
        if index:
            self.scroll_subscribers.pop(index)

    def call_scroll(self, movement: int):
        for sub in self.scroll_subscribers:
            sub(movement)

    async def run_app(self):
        with patch_stdout():
            await self.app.run_async()

    def start(self):
        if self._started:
            return

        self._started = True

        def runner():
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.run_app())

        threading.Thread(
            target=runner,
            daemon=True
        ).start()

    async def input_async(self, prompt=">>> ") -> str:
        self._prompt = prompt
        self._input_future = asyncio.get_running_loop().create_future()
        return await self._input_future

    def write(self, text):
        self.output_lines.append(text)
        self.app.invalidate()

    def draw_buffer(self, buffer: Buffer):
        rows = self.app.output.get_size().rows
        cols = self.app.output.get_size().columns
        self.output_lines = buffer.get_out_lines(rows, cols)
        self.app.invalidate()


async def main():
    cm = ConsoleManager()
    # Запускаем приложение и input в одном loop
    asyncio.create_task(cm.run_app())

    buf = Buffer()
    buf.top_lines.append("Start")
    cm.draw_buffer(buf)

    while True:
        text = await cm.input_async(">>> ")
        buf.out_text += "\n" + text
        cm.draw_buffer(buf)
        print(buf.get_out_lines(20, 100))

if __name__ == "__main__":
    asyncio.run(main())
