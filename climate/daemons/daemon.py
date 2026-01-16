import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from climate.app import App
    from climate.page.page import Page
    from climate.io.io import IO


class Daemon:
    _is_looping = False
    _interval = 1

    def __init__(self, app: "App",
                 page: Optional["Page"],
                 io: "IO",
                 is_looping: bool | None = None,
                 interval: int | None = None
                 ) -> None:
        self.app = app
        self.page = page
        self.io = io
        self.is_looping, self.interval = self._get_standard_value()
        if is_looping:
            self.is_looping = is_looping
        if interval:
            self.interval = interval

        self.looped = True

    @classmethod
    def _get_standard_value(cls) -> tuple[bool, int]:
        return cls._is_looping, cls._interval

    def main(self):
        """background process, ran in App"""
        pass

    def _looping(self):
        while self.looped and self.is_looping:
            self.loop()
            time.sleep(self.interval)

    def loop(self):
        """cycle background process, ran in App"""
        pass

    def stop(self):
        self.looped = False

    def start(self):
        self.looped = True
