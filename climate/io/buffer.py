from .template_string import TemplateString


class Buffer:
    def __init__(self) -> None:
        self.out_text: str = ""
        self.bottom_lines: list[str | TemplateString] = []
        self.top_lines: list[str | TemplateString] = []
        self.input_text: str = ""
        self.input_prefix: str | TemplateString = ""

    def get_out_lines(self, height: int, width: int) -> list[str]:
        out_lines: list[str] = []

        top_lines = []
        text_lines = []
        bottom_lines = []

        for top_line in self.top_lines:
            line_text = str(top_line)
            top_lines += self._normalize_line(width, line_text)

        for bottom_line in self.bottom_lines:
            line_text = str(bottom_line)
            bottom_lines += self._normalize_line(width, line_text)

        if len(top_lines) + len(bottom_lines) < height:
            height -= len(top_lines) + len(bottom_lines)
        else:
            out_lines = top_lines + bottom_lines
            out_lines = out_lines[:height]
            return out_lines

        for out_line in self.out_text.splitlines()[::-1]:
            lines = self._normalize_line(width, out_line)
            if len(lines) > height:
                text_lines += lines[:height]
                height = 0
            else:
                text_lines += lines
                height -= len(lines)

        text_lines.reverse()

        if height:
            text_lines += ["" for _ in range(height)]
        out_lines = top_lines + text_lines + bottom_lines
        return out_lines

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
    buf.out_text = "привет, бр бр, \n пппп \n вывв \n"
    buf.top_lines.append("ffff")
    buf.bottom_lines.append("ggg")
    print(buf.get_out_lines(10, 10))
