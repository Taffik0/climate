# CLIMATE - Python framework for terminal apps

**CliMate** is a framework for building full-screen terminal applications, where the bottom line is reserved for command input, and the rest of the screen is used for output. Suitable for console messengers, text-based RPGs, and live logs.

## Project Status ⚠️

- The library is in an early stage of development.
- The API is unstable and subject to change.
- Bugs and undocumented behaviors may occur.
- Documentation is a work in progress.

## Key Features

- **Page-based architecture** — a sequence of pages (MenuPage → MainPage → ExitPage) with separation of logic and state.
- **IO abstraction** — a high-level interface for output and input; you can use `io.print()` during user input without errors.
- **Daemon processes** — background tasks with safe console output.
- **TemplateString** — strings with placeholders and ANSI colors without manual formatting.

## CliMate is not intended for

- Creating graphical interfaces, buttons, or labels.
- Drawing arbitrary graphics (no Canvas support).
- Managing terminal window configuration.
- Replacing `prompt_toolkit`; CliMate uses it as a low-level foundation for its functionality.

## TemplateString

Allows you to:

- Use placeholders `${arg-name}`
- Apply ANSI colors via `@color` (`@red`, `@yellow`)

## Examples

### Minimal Page/App example

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

### Example of creating a Daemon on a page

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
