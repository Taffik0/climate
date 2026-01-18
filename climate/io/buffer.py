from .template_string import TemplateString


class Buffer:
    def __init__(self) -> None:
        self.out_text: list[str | TemplateString] = []
        self.bottom_lines: list[str | TemplateString] = []
        self.top_lines: list[str | TemplateString] = []
        self.input_text: str = ""
        self.input_prefix: str | TemplateString = ""

        self.offset: int = 0
        self.out_text_len = len(self.out_text)

        self.last_height = 10
        self.last_width = 10

    def get_out_lines(self, height: int, width: int) -> list[str]:
        self.last_height = height
        self.last_width = width

        # верхние и нижние линии
        top_lines = []
        bottom_lines = []
        for line in self.top_lines:
            top_lines += self._normalize_line(width, str(line))
        for line in self.bottom_lines:
            bottom_lines += self._normalize_line(width, str(line))

        # сколько места для основного текста
        content_height = max(height - len(top_lines) - len(bottom_lines), 0)

        # строим текст с запасом под offset
        text_lines = self.get_out_text(
            width, content_height + self.offset, self.out_text)
        text_len = len(text_lines)

        # ограничиваем offset, чтобы не уходить слишком далеко
        effective_offset = min(self.offset, max(text_len - content_height, 0))
        self.offset = effective_offset

        # берём видимые строки
        if effective_offset:
            visible_lines = text_lines[-(content_height +
                                         effective_offset):-effective_offset]
        else:
            visible_lines = text_lines[-content_height:]

        # добавляем пустые строки **только если текста меньше content_height даже при offset = 0**
        if len(text_lines) < content_height:
            visible_lines += [""] * (content_height - len(visible_lines))

        return top_lines + visible_lines + bottom_lines

    def get_out_text(self, width: int, height: int, out_text: list[str | TemplateString]) -> list[str]:
        out_lines: list[str] = []
        text_line = ""

        for chunk in reversed(out_text):
            s = str(chunk)

            while s:
                idx = s.rfind("\n")
                if idx != -1:
                    # всё после \n относится к текущей строке
                    text_line = s[idx + 1:] + text_line

                    # строка завершена, нормализуем БЕЗ \n
                    normalized = self._normalize_line(width, text_line)
                    for line in reversed(normalized):
                        out_lines.append(line)
                        if len(out_lines) >= height:
                            return list(reversed(out_lines))

                    text_line = ""
                    s = s[:idx]
                else:
                    text_line = s + text_line
                    s = ""

        # последняя незавершённая строка
        if text_line:
            normalized = self._normalize_line(width, text_line)
            for line in reversed(normalized):
                out_lines.append(line)
                if len(out_lines) >= height:
                    break

        return list(reversed(out_lines))

    def add_out_text(self, out: str | TemplateString):
        self.out_text.append(out)
        if self.offset:
            self.offset += len(self.get_out_text(self.last_width,
                               self.last_height,  [out]))

    def _normalize_line(self, width, text) -> list[str]:
        out_lines = []
        while len(text) >= width:
            out_lines.append(text[:width])
            text = text[width:]
        if text:
            out_lines.append(text)
        return out_lines


if __name__ == "__main__":
    buf = Buffer()
    buf.out_text = ["привет, бр бр, \n пппп \n вывв \n",
                    "fff", "\n\nh\nh\nh\nh"]
    buf.top_lines.append("ffff")
    buf.bottom_lines.append("ggg")
    buf.offset = 0
    print(buf.get_out_lines(10, 10))
