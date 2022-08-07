import re

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

class Optional(Argument):

  def __init__(self):
    super().__init__()
