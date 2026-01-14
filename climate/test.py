from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
import threading
import time

# Буфер для ввода
input_buffer = Buffer()

# Список строк для "живого вывода"
output_lines = ["Старт программы..."]


def get_output_text():
    return "\n".join(output_lines)


# Контролы
output_control = FormattedTextControl(get_output_text)
output_window = Window(content=output_control, height=10, wrap_lines=True)
input_window = Window(content=BufferControl(buffer=input_buffer))

# Layout: вывод сверху, ввод снизу
layout = Layout(HSplit([output_window, input_window]))

# Keybindings: Enter = завершение ввода
kb = KeyBindings()


@kb.add("enter")
def accept(event):
    output_lines.append("Вы ввели: " + input_buffer.text)
    input_buffer.text = ""


# Создаём приложение
app: Application = Application(
    layout=layout, key_bindings=kb, full_screen=True)

# Фоновая задача, которая обновляет вывод


def background_task():
    i = 0
    while True:
        i += 1
        time.sleep(1)
        output_lines.append(f"Счётчик: {i}")
        app.invalidate()  # перерисовать экран


threading.Thread(target=background_task, daemon=True).start()

# Запуск приложения
with patch_stdout():
    app.run()
