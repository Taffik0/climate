from typing import TYPE_CHECKING, Callable, Optional, TypeVar

if TYPE_CHECKING:
    from ..app import App
    from .page_data import PageData
    from .reverse_data import ReverseData

from ..io.io import IO

InD = TypeVar("InD", bound="PageData")
RD = TypeVar("RD", bound="ReverseData")


class Page:
    _name_ = None

    def __init__(self, app: "App",
                 page_data: InD,
                 parent: "Page" | None = None,
                 reverse_func: Optional[Callable[[InD, Optional[RD]], None]] = None):
        self.app = app
        self.io = IO(page=self)
        self.commands: list = []
        self.out_prefix = ""
        self.parent = parent
        self.reverse_func = reverse_func
        self.page_data = page_data
        self._init()
        self.on_enter()

    def _init(self):
        pass

    def on_enter(self):
        pass

    def on_exit(self) -> None:
        pass

    def loop(self):
        pass

    def exit(self, reverse_data: Optional[RD] = None) -> None:
        self.on_exit()
        if callable(self.reverse_func):
            self.reverse_func(self.page_data, reverse_data)
        self.app.change_page(self.parent)

    def switch_loop(self, page: "Page"):
        self.app.change_page(page)
