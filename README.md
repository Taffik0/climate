# CLIMATE - python framework for terminal app

⚠️ Статус проекта

- Библиотека находится на ранней стадии разработки.
- API нестабилен и может меняться.
- Возможны баги и недокументированные особенности.
- Документация в процессе.

**CliMate** — фреймворк для создания полноэкранных терминальных приложений, где нижняя строка предназначена для ввода команд, а остальная область используется для вывода.

Основные возможности:

- **Page-based архитектура**  
   Позволяет строить приложение как последовательность страниц (MenuPage → MainPage → ExitPage), разделяя логику и состояние.
- **Абстракция ввода-вывода (IO)**  
   Высокоуровневый интерфейс для вывода и ввода. Можно вызывать `print()` даже во время пользовательского ввода без нарушения состояния консоли.
- **Daemon-процессы**  
   Фоновые задачи с возможностью безопасного вывода в консоль, например для отображения состояния процессов.
- **TemplateString**  
   Шаблонные строки с плейсхолдерами и ANSI-цветами без ручного форматирования.

**CliMate не предназначен для:**

- Создания графических интерфейсов. Кнопок, лейблов и layout-систем нет и не планируется.
- Рисования произвольной графики. Canvas отсутствует.
- Управления конфигурацией окна терминала.
- Замены prompt_toolkit. CliMate использует его как низкоуровневую основу, но решает другую задачу.

**TemplateString** позволяет:

- использовать плейсхолдеры `${arg-name}`
- применять ANSI-цвета через `@color` (например `@red`, `@yellow`)

Пример:

```python
import time
from climate import App, Page, PageData
from climate.io import TemplateString
from climate.daemons import Daemon


class WriteDaemon(Daemon):
    _is_looping = True
    _interval = 1

    def main(self):
        self.count = 0
        self.io.print(TemplateString(
            "@yellow ${count}x Hello").string({"count": 0}))

    def loop(self):
        self.count += 1
        self.io.print(TemplateString(
            "@yellow ${count}x Hello").string({"count": self.count}))


class MainPage(Page):

    def on_enter(self):
        self.io.print("Hello")
        daemon = WriteDaemon(self.app, self, self.io)
        self.app.add_daemon(daemon)

    def init(self):
        self.scrollable = True

    def loop(self):
        text = self.io.input(">>>")
        self.io.print(text)


app = App()
app.set_start_page(MainPage(app, PageData()))
app.start()
```
