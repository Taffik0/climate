from .io import IO
from .template_string import TemplateString


class Sayer:
    def __init__(self, io: IO, name: str, out_temp: TemplateString | None = None):
        self.io = io
        self.out_temp = out_temp
        self.name = name

    def say(self, text: str | TemplateString):
        self.io.say(text, self.name, out_temp=self.out_temp)
