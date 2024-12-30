from curses import curs_set, echo, initscr, noecho, window, color_pair, init_pair, has_colors, start_color
from curses import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, A_BOLD, COLOR_GREEN, COLOR_BLACK
from file import File


class Editor:
  """
  Handles the editor's main loop, drawing, and user input.
  """

  def __init__(self, _file: File) -> None:
    self.file = _file
    self.content = _file.content
    self.cursor_pos = 0
    self.start_line = 0
    self.bytes_per_line = 16

    self.help_message = [  # Empty strings serve as line breaks.
      "CLX Help",
      "",
      "q: Quit",
      "e: Edit byte",
      "w: Save",
      "g: Jump to address",
      "a: Add bytes",
      "i: Insert bytes",
      "r: Remove selected byte",
      "",
      "Use arrow keys to navigate.",
    ]

    initscr()
    if has_colors():  # Enable colors if supported.
      start_color()
      # Define color pair 1 as green text on black background.
      init_pair(1, COLOR_GREEN, COLOR_BLACK)

  def draw(self, _stdscr: window, _path: str) -> None:
    """ Draws the editor. """

    _stdscr.clear()

    height, width = _stdscr.getmaxyx()

    # Draw the top bar with the file path.
    top_bar = f"Editing {_path}"
    _stdscr.addstr(0, 0, top_bar[:width])

    # Reserve space for status bar and top bar.
    lines_to_display = height - 3

    # Draw the file content in hex and ASCII.
    for i in range(lines_to_display):
      offset = (self.start_line + i) * self.bytes_per_line
      if offset >= len(self.content): break

      # Hex side.
      hex_bytes = ' '.join(f"{byte:02X}" for byte in self.content[offset:offset + self.bytes_per_line])
      # This is a string formatting syntax that
      # left-aligns the string to a width of 48 characters.
      _stdscr.addstr(i + 1, 0, f"{offset:08X}  {hex_bytes:<48}")

      # ASCII side.
      # The condition is a ternary operator that
      # checks if the byte is a printable ASCII character.
      ascii_bytes = ''.join(
        chr(byte) if 32 <= byte < 127 else "." for byte in self.content[offset:offset + self.bytes_per_line]
      )
      _stdscr.addstr(i + 1, 60, ascii_bytes)

      if self.start_line + i == self.cursor_pos // self.bytes_per_line:
        cursor_column = (self.cursor_pos % self.bytes_per_line) * 3 + 10
        if has_colors():
          _stdscr.addstr(i + 1, cursor_column, f"{self.content[self.cursor_pos]:02X}", color_pair(1) | A_BOLD)
          _stdscr.addstr(i + 1, 60 + (self.cursor_pos % self.bytes_per_line), ascii_bytes[self.cursor_pos % self.bytes_per_line], color_pair(1) | A_BOLD)
        else:
          _stdscr.addstr(i + 1, cursor_column, f"{self.content[self.cursor_pos]:02X}", A_BOLD)
          _stdscr.addstr(i + 1, 60 + (self.cursor_pos % self.bytes_per_line), ascii_bytes[self.cursor_pos % self.bytes_per_line], A_BOLD)

    # Draw the cursor position.
    # This calculates the cursor's position in the hex view.
    cursor_line = (self.cursor_pos // self.bytes_per_line) - self.start_line

    # 3 spaces per byte in hex view.
    cursor_column = (self.cursor_pos % self.bytes_per_line) * 3 + 10

    if 0 <= cursor_line < lines_to_display: _stdscr.move(cursor_line + 1, cursor_column)

    # Draw the status bar.
    status = f"Cursor: {self.cursor_pos:08X} | Size: {len(self.content)} bytes | 'h' for help."
    _stdscr.addstr(_stdscr.getmaxyx()[0] - 1, 0, status[:_stdscr.getmaxyx()[1]])

    _stdscr.refresh()

  def success(self, _stdscr: window, _message: str) -> None:
    height, width = _stdscr.getmaxyx()
    win_height, win_width = 3, len(_message) + 4
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    success_window = _stdscr.subwin(win_height, win_width, start_y, start_x)
    success_window.clear()
    success_window.border()
    success_window.addstr(1, 2, _message)
    success_window.refresh()
    _stdscr.getch()  # Wait for user input to close the window.
    _stdscr.clear()

  def error(self, _stdscr: window, _message: str) -> None:
    height, width = _stdscr.getmaxyx()
    win_height, win_width = 3, len(_message) + 4
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    error_window = _stdscr.subwin(win_height, win_width, start_y, start_x)
    error_window.clear()
    error_window.border()
    error_window.addstr(1, 2, _message)
    error_window.refresh()
    _stdscr.getch()  # Wait for user input to close the window.
    _stdscr.clear()

  def clx_help(self, _stdscr: window) -> None:  # 'h'.
    """ Help menu. """

    height, width = _stdscr.getmaxyx()
    win_height, win_width = len(self.help_message) + 2, 54
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    help_win = _stdscr.subwin(win_height, win_width, start_y, start_x)
    help_win.clear()
    help_win.border()

    for i, line in enumerate(self.help_message):
      if len(line) < 1: continue
      help_win.addstr(i+1, 1, line)

    help_win.refresh()
    _stdscr.getch()  # Wait for user input to close the window.
    _stdscr.clear()

  def edit(self, _stdscr: window) -> None:  # 'e'.
    """ Allows you to edit the byte at the cursor position. """

    height, width = _stdscr.getmaxyx()
    win_height, win_width = 3, 20
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    edit_win = _stdscr.subwin(win_height, win_width, start_y, start_x)
    edit_win.clear()
    edit_win.border()
    edit_win.addstr(1, 1, "Enter hex: ")
    edit_win.refresh()
    echo()
    new_value = edit_win.getstr(1, 11, 2).decode("utf-8")
    noecho()
    _stdscr.clear()

    try: self.content[self.cursor_pos] = int(new_value, 16)
    except ValueError: ...
    _stdscr.clear()

  def save(self, _stdscr: window) -> None:  # 'w'.
    """ Writes content back to the file. """

    try:
      self.file.write(bytes(self.content))
      self.success(_stdscr, f"Wrote {len(self.content)} bytes!")
    except: self.error(_stdscr, "Failed to save! This may be a read-only file.")

  def jump_to_address(self, _stdscr: window) -> None:  # 'g'.
    """ Jumps to a specific address in the file (ex. 1A). """

    height, width = _stdscr.getmaxyx()
    win_height, win_width = 3, 80
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    jump_win = _stdscr.subwin(win_height, win_width, start_y, start_x)
    jump_win.clear()
    jump_win.border()
    jump_win.addstr(1, 1, "Enter hex address: ")
    jump_win.refresh()
    echo()
    address = jump_win.getstr(1, 22, 8).decode("utf-8")
    noecho()
    _stdscr.clear()

    try:
      self.cursor_pos = int(address, 16)
      if self.cursor_pos >= len(self.content): self.cursor_pos = len(self.content) - 1

      # Adjust the visible window.
      if self.cursor_pos < self.start_line * self.bytes_per_line:self.start_line = self.cursor_pos // self.bytes_per_line
      elif self.cursor_pos >= (self.start_line + _stdscr.getmaxyx()[0] - 2) * self.bytes_per_line: self.start_line = self.cursor_pos // self.bytes_per_line - (_stdscr.getmaxyx()[0] - 3)
    except ValueError:
      self.error(_stdscr, "Invalid address!")

  def add_bytes(self, _stdscr: window) -> None:  # 'a'.
    """ Appends bytes to the end of the file. """

    height, width = _stdscr.getmaxyx()
    win_height, win_width = 3, 50
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    add_win = _stdscr.subwin(win_height, win_width, start_y, start_x)
    add_win.clear()
    add_win.border()
    add_win.addstr(1, 1, "Number of bytes: ")
    add_win.refresh()
    echo()
    num_bytes = add_win.getstr(1, 22, 8).decode("utf-8")
    noecho()
    _stdscr.clear()

    try:
      num_bytes = int(num_bytes)
      self.content.extend(bytearray(num_bytes))
    except ValueError:
      self.error(_stdscr, "Invalid number!")
    _stdscr.clear()

  def insert_bytes(self, _stdscr: window) -> None:  # 'i'.
    """ Inserts bytes at the cursor position. """

    height, width = _stdscr.getmaxyx()
    win_height, win_width = 3, 50
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    insert_win = _stdscr.subwin(win_height, win_width, start_y, start_x)
    insert_win.clear()
    insert_win.border()
    insert_win.addstr(1, 1, "Number of bytes: ")
    insert_win.refresh()
    echo()
    num_bytes = insert_win.getstr(1, 22, 8).decode("utf-8")
    noecho()
    _stdscr.clear()

    try:
      num_bytes = int(num_bytes)
      self.content[self.cursor_pos:self.cursor_pos] = bytearray(num_bytes)
    except ValueError:
      self.error(_stdscr, "Invalid number!")
    _stdscr.clear()

  def remove_byte(self, _stdscr: window) -> None:
    """ Deletes the byte at the cursor position, and shifts the cursor back 1. """

    if len(self.content) > 0:
      del self.content[self.cursor_pos]
      self.cursor_pos = max(0, self.cursor_pos - 1)

    _stdscr.clear()

  def main(self, _stdscr: window, _path: str) -> None:
    """ Main loop, handles calling all other methods and user input. """

    curs_set(1)  # Show cursor.
    _stdscr.keypad(True)

    while True:
      self.draw(_stdscr, self.file.path)

      # Handle user input.
      # I tried to use match-case but all I got was "called match pattern must be a class".
      key = _stdscr.getch()
      if key == ord("q"): break
      if key == ord("h"): self.clx_help(_stdscr)
      if key == ord("e"): self.edit(_stdscr)
      if key == ord("w"): self.save(_stdscr)
      if key == ord("g"): self.jump_to_address(_stdscr)
      if key == ord("a"): self.add_bytes(_stdscr)
      if key == ord("i"): self.insert_bytes(_stdscr)
      if key == ord("r"): self.remove_byte(_stdscr)
      if key == KEY_DOWN: self.cursor_pos += self.bytes_per_line
      if key == KEY_UP: self.cursor_pos -= self.bytes_per_line
      if key == KEY_LEFT: self.cursor_pos -= 1
      if key == KEY_RIGHT: self.cursor_pos += 1

      # Ensure cursor_pos is within bounds.
      self.cursor_pos = max(0, min(len(self.content) - 1, self.cursor_pos))

      # Adjust the visible window.
      if self.cursor_pos < self.start_line * self.bytes_per_line: self.start_line -= 1
      elif self.cursor_pos >= (self.start_line + _stdscr.getmaxyx()[0] - 3) * self.bytes_per_line: self.start_line += 1
