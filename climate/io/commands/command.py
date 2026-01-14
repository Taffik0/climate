class Flag:
    def __init__(self, name: str, kwarg: str | None):
        if len(name) > 1:
            raise
        self.name = name
        self.kwarg = kwarg


class WordFlag(Flag):
    def __init__(self, name: str, kwarg: str):
        self.name = name
        self.kwarg = kwarg


class Command:
    def __init__(self, method, name: str, flags: list[Flag]):
        self.method = method
        self.name = name
        self.flags = flags
