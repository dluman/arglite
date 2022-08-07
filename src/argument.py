import re

from typing import Any

class Argument:

  def __init__(self, line: str = ""):
    self.line = line

  def __getattribute__(self, name) -> Any:
    try:
      attr = super().__getattribute__(name)
      return attr
    except AttributeError:
      print(f"✗ ERROR: The required a value for {name}, but didn't receive one!")

  def required(self, required: bool = False):
    regexp = re.compile("\.optional\.")
    result = re.match(regexp, self.line)
    if required and result:
      return False
    return True

class Required(Argument):

  def __init__(self):
    super().__init__()

class Optional(Argument):

  def __init__(self):
    super().__init__()

  def __getattribute__(self, name) -> Any:
    try:
      attr = super().__getattribute__(name)
      return attr
    except AttributeError:
      return 0
