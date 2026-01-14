import re
from typing import Any

from .ansi_colors import COLORS


class TemplateString:
    def __init__(self, text: str):
        self.text = text

    def string(self, args: dict[str, Any] = {}) -> str:
        text = self.text
        for match in re.finditer(r"\$\{(.*?)\}", text):
            key = match.group(1)
            agr = args.get(key)
            if not agr:
                agr = ""
            text = text.replace("${"+key+"}", agr)
        text = self._parse_colors(text)
        return text

    def _parse_colors(self, text: str):
        for match in re.finditer(r"\@(\w+)\s?", text):
            key = match.group(1)
            color = COLORS.get(key)
            if not color:
                color = ""
            text = text.replace(match.group(0), color)
        text += COLORS["r"]
        return text

    def __str__(self):
        return self.string()


if __name__ == "__main__":
    tstr = TemplateString("Hello @yellow ${name}@r  br br")
    print(tstr.string({"name": "yarilo"}))
