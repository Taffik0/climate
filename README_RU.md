# CLIMATE - Python framework for terminal apps

**CliMate** — фреймворк для создания полноэкранных терминальных приложений, где нижняя строка предназначена для ввода команд, а остальная область используется для вывода. Подходит для консольных мессенджеров, текстовых RPG и live-логов.

## Статус проекта ⚠️

- Библиотека находится на ранней стадии разработки.
- API нестабилен и может меняться.
- Возможны баги и недокументированные особенности.
- Документация в процессе.

## Основные возможности

- **Page-based архитектура** — последовательность страниц (MenuPage → MainPage → ExitPage) с разделением логики и состояния.
- **Абстракция ввода-вывода (IO)** — высокоуровневый интерфейс для вывода и ввода; можно использовать `io.print()` во время пользовательского ввода без ошибок.
- **Daemon-процессы** — фоновые задачи с безопасным выводом в консоль.
- **TemplateString** — строки с плейсхолдерами и ANSI-цветами без ручного форматирования.

## CliMate не предназначен для

- Создания графических интерфейсов, кнопок или лейблов.
- Рисования произвольной графики (Canvas отсутствует).
- Управления конфигурацией окна терминала.
- Замены prompt_toolkit; CliMate использует его как низкоуровневую основу для своих задач.

## TemplateString

Позволяет:

- Использовать плейсхолдеры `${arg-name}`
- Применять ANSI-цвета через `@color` (`@red`, `@yellow`)

## Примеры

### Минимальный пример Page/App

```python
from climate import App, Page, PageData

class MainPage(Page):
    def loop(self):
        text = self.io.input(">>> ")
        self.io.print(f"Вы ввели: {text}")

app = App()
app.set_start_page(MainPage(app, PageData()))
app.start()
```

### TemplateString:

```python
from climate.io import TemplateString

ts = TemplateString("@green Hello, ${name}!", {"name": "Taffik"})
print(ts.string())
```

### Пример создания Daemon в странице

```python
from climate.daemons import Daemon
from climate import App, Page, PageData
from climate.io import TemplateString

class CounterDaemon(Daemon):
    _is_looping = True
    _interval = 1

    def main(self):
        self.count = 0

    def loop(self):
        self.count += 1
        self.io.print(TemplateString("@yellow ${count}x Hello").string({"count": self.count}))

class MainPage(Page):
    def on_enter(self):
        daemon = CounterDaemon(self.app, self, self.io)
        self.app.add_daemon(daemon)
        self.io.print("Daemon запущен!")

app = App()
app.set_start_page(MainPage(app, PageData()))
app.start()
```
