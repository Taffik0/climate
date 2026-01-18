import shutil
import sys


class OutManager:
    def clear(self):
        sys.stdout.write("\x1b[2J")
        sys.stdout.flush()

    def clear_current_line(self):
        sys.stdout.write("\x1b[2K")
        sys.stdout.flush()

    def enter(self):
        sys.stdout.write("\x1b[?1049h\x1b[?7l")
        sys.stdout.flush()

    def exit(self):
        sys.stdout.write("\x1b[?1049l")
        sys.stdout.flush()

    def get_size(self) -> tuple[int, int]:
        size = shutil.get_terminal_size()
        cols = size.columns
        rows = size.lines
        return cols, rows
