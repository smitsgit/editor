import sys
import curses

import termios
import tty
import copy

stdscr = curses.initscr()

special_char = {
    17: '^q',
    6: '^f',
    2: '^b',
    21: '^u',
    4: '^d',
    120: '^l',
    18: '^r',
}


class Editor:
    def __init__(self, file):
        with open(file, "r") as fp:
            lines = fp.readlines()
        self.buffer = Buffer(lines)
        self.row = 0
        self.col = 0
        self.cursor = Cursor()
        self.history = []

    def run(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        while True:
            self.render()
            self.handle_input()

        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def render(self):
        self.clear_screen()
        self.move_cursor(self.row, self.col)
        self.buffer.render()
        self.move_cursor(self.cursor.row, self.cursor.col)

    def handle_input(self):
        c = sys.stdin.read(1)
        print(ord(c))
        if special_char.get(ord(c)) == '^q':
            sys.exit(0)
        elif special_char.get(ord(c)) == '^f':
            self.cursor = self.cursor.forward(self.buffer)
        elif special_char.get(ord(c)) == '^b':
            self.cursor = self.cursor.backward(self.buffer)
        elif special_char.get(ord(c)) == '^u':
            self.cursor = self.cursor.up()
        elif special_char.get(ord(c)) == '^d':
            self.cursor = self.cursor.down(self.buffer)
        elif special_char.get(ord(c)) == '^r':
            self.restore_snapshot()
        elif ord(c) == 127:
            self.buffer = self.buffer.delete(c, self.cursor.row, self.cursor.col)
            self.cursor = self.cursor.left(self.buffer)
            self.save_snapshot()
        else:
            self.buffer = self.buffer.insert(c, self.cursor.row, self.cursor.col)
            self.cursor = self.cursor.right(self.buffer)
            self.save_snapshot()

    def clear_screen(self):
        print("\033[2J")

    def move_cursor(self, row, col):
        print("\033[{};{}H".format(row + 1, col + 1))

    def save_snapshot(self):
        self.history.append((self.buffer, self.cursor))

    def restore_snapshot(self):
        if self.history:
            self.buffer, self.cursor = self.history.pop()


class Buffer:
    """Represents the contents of the file"""

    def __init__(self, lines):
        self.lines = lines

    def insert(self, chr, row, col):
        new_lines = copy.deepcopy(self.lines)
        line = new_lines[row]
        lst = list(line)
        lst.insert(col, chr)
        new_lines[row] = "".join(lst)
        return Buffer(new_lines)

    def delete(self, chr, row, col):
        new_lines = copy.deepcopy(self.lines)
        line = new_lines[row]
        lst = list(line)
        del(lst[col])
        new_lines[row] = "".join(lst)
        return Buffer(new_lines)

    def render(self):
        for line in self.lines:
            line = line.replace("\n", "\r\n")
            print(line, end='')

    def lines_count(self):
        return len(self.lines)

    def line_length(self, row):
        print(len(self.lines[row]))
        print(len(self.lines[row]))
        return len(self.lines[row])


class Cursor:
    """Represents the cursor position and handles the cursor movements.
       This is going to have a fair bit of behaviour than just the cursor data"""

    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def up(self):
        if self.row - 1 < 0:
            return Cursor(0, self.col)
        else:
            return Cursor(self.row - 1, self.col)

    def down(self, buffer):
        if self.row + 1 > buffer.lines_count():
            return Cursor(self.row, self.col)
        else:
            return Cursor(self.row + 1, self.col)

    def forward(self, buffer):
        if self.col + 1 > buffer.line_length(self.row):
            return Cursor(self.row, self.col)
        else:
            return Cursor(self.row, self.col + 1)

    def backward(self, buffer):
        if self.col - 1 < 0:
            return Cursor(self.row, self.col)
        else:
            return Cursor(self.row, self.col - 1)

    def right(self, buffer):
        return Cursor(self.row, self.col + 1)

    def left(self, buffer):
        return Cursor(self.row, self.col - 1)

    def __repr__(self):
        return "Cursor({},{})".format(self.row, self.col)


def main():
    editor = Editor("foo.txt")
    editor.run()


if __name__ == '__main__':
    main()
