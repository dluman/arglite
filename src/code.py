import re
import inspect

from .argument import Argument
from importlib import abc

class Code:

  def __init__(self, file):
    with open(file, "r") as fh:
        self.source = fh.readlines()
    self.name = self.find_import()
    self.partial = self.check_partial()

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

  def check_status(self, expr: str = "") -> bool:
    """ Check if a var is required or optional per invoking codebase """
    arg = Argument(expr)
    return arg.required()
