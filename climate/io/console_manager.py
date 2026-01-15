import asyncio
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer as TBuffer
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout

from .buffer import Buffer


class ConsoleManager:
    def __init__(self):
        self.loop = asyncio.new_event_loop()  # только создаём

        self.input_buffer = TBuffer()
        self.output_lines = []
        self._prompt = ">>> "
        self._input_future = None

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

        @kb.add("enter")
        def accept(event):
            if self._input_future and not self._input_future.done():
                self._input_future.set_result(self.input_buffer.text)
            self.input_buffer.text = ""

        self.app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True
        )

    async def run_app(self):
        with patch_stdout():
            await self.app.run_async()

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
