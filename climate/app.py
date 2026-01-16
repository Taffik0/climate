from threading import Thread

from .io.console_manager import ConsoleManager

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .page.page import Page
    from climate.daemons.daemon import Daemon


class App:
    def __init__(self) -> None:
        self.pages: dict[str, "Page"] = {}  # сделать потом!!!
        self.active_page: "Page" | None = None
        self.start_page: "Page" | None = None
        self.commands: list = []
        self.console_manager = ConsoleManager()
        self.console_manager.start()

        self.daemons: list[Daemon] = []
        self.daemon_process: list[Thread] = []

    """    def add_page(self, page: "Page", name: str | None = None):
        if name:
            self.pages[name] = page(self)
        elif page._name_:
            self.pages[page._name_] = page(self)
        else:
            print("Error, page have not name") переделать!!!"""

    def set_start_page(self, page: "Page"):
        self.start_page = page

    def change_page(self, page: Page | None):
        self.active_page = page

    def start(self):
        if not self.start_page:
            return
        self.active_page = self.start_page
        self.looping()

    def looping(self):
        while self.active_page:
            self._main_loop()

    def _main_loop(self):
        self.active_page.loop()

    def add_daemon(self, daemon: Daemon):
        self.daemons.append(daemon)
        main_thread = Thread(target=daemon.main, daemon=True)
        main_thread.start()
        self.daemon_process.append(main_thread)
        if daemon.is_looping:
            loop_thread = Thread(target=daemon._looping, daemon=True)
            self.daemon_process.append(loop_thread)
            loop_thread.start()
