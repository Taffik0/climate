from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar

from climate.page.page_exit_exception import PageExit

if TYPE_CHECKING:
    from ..app import App
    from .page_data import PageData
    from .reverse_data import ReverseData
    from climate.io.commands.command import Command

from ..io.io import IO

InD = TypeVar("InD", bound="PageData")
RD = TypeVar("RD", bound="ReverseData")


class Page(Generic[InD, RD]):
    _name_ = None

    def __init__(self, app: "App",
                 page_data: InD,
                 parent: Optional["Page"] = None,
                 reverse_func: Optional[Callable[[InD, Optional[RD]], None]] = None):
        self.app = app
        self.commands: list["Command"] = []
        self.command_prefix: str = "/"
        self.out_prefix = ""
        self.scrollable = False
        self.parent = parent
        self.reverse_func = reverse_func
        self.page_data = page_data
        self.exited = False
        self._init()
        self.io = IO(page=self, app=app)

    def _init(self):
        if self.exited:
            self.io.restart()
        self.init()

    def init(self):
        pass

    def _on_enter(self):
        self.on_enter()

    def on_enter(self):
        pass

    def _on_exit(self) -> None:
        self.io.exit()
        self.exited = True
        self.on_exit()

    def on_exit(self) -> None:
        pass

    def loop(self):
        pass

    def exit(self, reverse_data: Optional[RD] = None, stop: bool = True) -> None:
        self._on_exit()
        if callable(self.reverse_func):
            self.reverse_func(self.page_data, reverse_data)
        self.app.change_page(self.parent)
        if stop:
            raise PageExit()

    def switch_page(self, page: "Page", stop: bool = True):
        self.app.change_page(page)
        if stop:
            raise PageExit()

    def switch_child_page(self, page: "Page", stop: bool = True):
        page.parent = self
        self.app.change_page(page)
        if stop:
            raise PageExit()
