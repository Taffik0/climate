from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, TypeVar, Generic


if TYPE_CHECKING:

    from ..events.event import Event
    from ..core.game import Game
    from .reverse_data import ReverseData

InT = TypeVar("InT", bound="Event")
RD = TypeVar("RD", bound="ReverseData")


class EventLoop(Generic[InT, RD]):
    def __init__(
        self,
        game: "Game",
        event: InT,
        parent: Optional["EventLoop"] = None,
        reverse_func: Optional[Callable[[InT, Optional[RD]], None]] = None,
    ):
        self.parent = parent
        self.game = game
        self.reverse_func = reverse_func
        self.event = event

    def loop(self) -> None:
        pass

    def exit(self, reverse_data: Optional[RD] = None) -> None:
        self.on_exit()
        if callable(self.reverse_func):
            self.reverse_func(self.event, reverse_data)
        self.game.set_loop(self.parent)

    def switch_loop(self, event_loop: "EventLoop"):
        self.game.set_loop(event_loop)

    def switch_child_loop(self, event_loop: "EventLoop"):
        event_loop.parent = self
        self.game.set_loop(event_loop)

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass
