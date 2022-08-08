import re

from typing import Any

class Argument:

  def __init__(self, line: str = ""):
    self.line = line

  def required(self, required: bool = False):
    regexp = re.compile("\.optional\.")
    result = re.match(regexp, self.line)
    if required and result:
      return False
    return True

class Required(Argument):

  def __init__(self):
    super().__init__()

  def __getattribute__(self, name) -> Any:
    try:
      return super().__getattribute__(name)
    except AttributeError:
      pass

class Optional(Argument):

  def __init__(self):
    super().__init__()

  def __getattribute__(self, name) -> Any:
    try:
      return super().__getattribute__(name)
    except AttributeError:
      return None

class RequirementError(Exception):

  def __init__(self, name, *args):
    super().__init__(args)
