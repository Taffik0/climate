from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer as TBuffer
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
import threading
import time

from .buffer import Buffer


class ConsoleManager:
    def __init__(self):
        self.input_buffer = TBuffer()
        self.output_lines = []

        self._input_event = threading.Event()
        self._input_result = None
        self._prompt = ">>> "

        def get_output_text():
            return "\n".join(self.output_lines)

        def prompt_func():
            return self._prompt

        output_control = FormattedTextControl(get_output_text)
        output_window = Window(content=output_control, wrap_lines=True)

        input_control = BufferControl(
            buffer=self.input_buffer,
            input_processors=[
                BeforeInput(lambda: self._prompt)
            ]
        )
        input_window = Window(content=input_control)

        layout = Layout(HSplit([output_window, input_window]))

        kb = KeyBindings()

        @kb.add("enter")
        def accept(event):
            self._input_result = self.input_buffer.text
            self.input_buffer.text = ""
            self._input_event.set()

        self.app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True
        )

    def start(self):
        threading.Thread(target=self._run_app, daemon=True).start()

    def _run_app(self):
        with patch_stdout():
            self.app.run()

    def input(self, prompt=">>> ") -> str:
        self._prompt = prompt
        self._input_event.clear()
        self.app.invalidate()

        self._input_event.wait()
        return self._input_result

    def write(self, text):
        self.output_lines.append(text)
        self.app.invalidate()

    def draw_buffer(self, buffer: Buffer):
        rows = self.app.output.get_size().rows
        cols = self.app.output.get_size().columns
        self.output_lines = buffer.get_out_lines(rows, cols)
        self.app.invalidate()

    def get_size(self) -> tuple[int, int]:
        rows = self.app.output.get_size().rows
        cols = self.app.output.get_size().columns
        return cols, rows


if __name__ == "__main__":
    buf = Buffer()
    buf.top_lines.append("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    cm = ConsoleManager()
    cm.start()
    cm.draw_buffer(buf)
    while True:
        buf.out_text += "\n" + cm.input()
        cm.draw_buffer(buf)
        print(buf.get_out_lines(20, 100))
