import re
import sys
import inspect

from typing import Any
from ast import literal_eval
from rich.table import Table
from rich.console import Console

class Parser:

  def __init__(self):
    self.file = sys.argv[0]
    arg_str = self.flatten(sys.argv[1:])
    self.args = self.pairs(arg_str)
    self.set_vars()

  def flatten(self, args: list = []) -> str:
    return " ".join(args)

  def pairs(self, args: str = "") -> list:
    return re.findall(r"-{1,2}([^-][a-z]*(?:\s)?)([^-]*)", args)

  def typify(self, val: Any) -> Any:
    try:
      val = literal_eval(val)
    except:
      pass
    return val

  def set_vars(self) -> None:
    self.vars = []
    for arg, val in self.args:
      if not val: val = True
      if type(val) == str: val = val.strip()
      arg = arg.strip()
      self.vars.append(arg)
      setattr(self, arg, self.typify(val))

  def display(self) -> None:
    table = Table(title="CLI flags")
    table.add_column("Variable name")
    table.add_column("Variable value")
    table.add_column("Variable type")

    for var in self.vars:
      val = getattr(self, var)
      table.add_row(
        var,
        str(val),
        type(val).__name__
      )

    console = Console()
    console.print(table)

parser = Parser()
