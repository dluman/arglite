import re

class Argument:

  def __init__(self, line: str = ""):
    self.line = line
    self.require = {
      True: f"(.required)?.",
      False: f".optional."
    }

  def required(self, required: bool = True):
    regexp = re.compile(self.require[required])
    result = re.match(regexp, self.line)
    print(self.line, regexp)
    if required and result:
      return True
    print(required, result)
    return False

class Required(Argument):

  def __init__(self):
    super().__init__()

class Optional(Argument):

  def __init__(self):
    super().__init__()
