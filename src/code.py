import re
import importlib
import inspect

class Code:

  def __init__(self, file):
    contents = importlib.abc.InspectLoader.source_to_code(
      "string",
      path = file
    )
    self.source = self.inspect(contents)
    self.name = self.find_import()
    self.partial = self.check_partial()
    self.checks = self.check_flags()

  def inspect(self, contents: str = "") -> list:
    """ Break the code into individual lines to scan """
    lines = inspect.getsourcelines(contents)[0]
    return [line.strip() for line in lines if line.strip() != ""]

  def find_import(self) -> str:
    """ Figure out how a user imports the module to scan code """
    exp = r"as\s(\b[a-z0-9_]+\b)"
    regex = re.compile(exp, re.I)
    for line in self.source:
      lib_import = re.search(regex, line)
      if lib_import: return lib_import.groups()[-1]
    return "arglite"

  def check_partial(self) -> bool:
    """ Special check if the import is from ... """
    if self.name != "arglite":
      exp = r"from\sarglite"
      regex = re.compile(exp)
      for line in self.source:
        if re.match(regex, line):
          return True
    return False

  def check_flags(self):
    """ Future feature for checking provided flags against existing """
    pass
