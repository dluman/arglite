import re
import sys

from typing import Any
from ast import literal_eval

class Parser:

  def __init__(self):
    self.file = sys.argv[0]
    arg_str = self.flatten(sys.argv[1:])
    self.args = self.pairs(arg_str)
    self.vars()

  def flatten(self, args: list = []) -> str:
    return " ".join(args)

  def pairs(self, args: str = []) -> list:
    return re.findall(r"-{1,2}([^-][a-z]*(?:\s)?)([^-]*)", args)

  def typify(self, val) -> Any:
    try:
      val = literal_eval(val)
    except:
      pass
    return val

  def vars(self) -> None:
    for arg, val in self.args:
      if not val: val = True
      if type(val) == str: val = val.strip()
      setattr(self, arg.strip(), self.typify(val))

parser = Parser()
