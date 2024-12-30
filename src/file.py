from os.path import abspath, exists, isdir


class File:
  """
  Represents a file that can be read from and (possibly) written to.
  """

  def __init__(self, _path):
    _path = abspath(_path)
    self.path = _path
    self.content = self.read()

    if not exists(_path): raise FileNotFoundError(f"'{_path}' not found.")
    if isdir(_path): raise IsADirectoryError(f"'{_path}' is a directory.")

  def read(self) -> bytearray:
    with open(self.path, "rb") as f: return bytearray(f.read())

  def write(self, _content: bytes):
    with open(self.path, "wb") as f: f.write(_content)
