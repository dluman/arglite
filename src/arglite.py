import re
import os
import sys
import inspect
import importlib

from typing import Any
from ast import literal_eval

from rich import print
from rich.table import Table
from rich.console import Console
from rich.markdown import Markdown

from .code import Code

class Parser:

  def __init__(self):
    """ Entry point. """
    self.file = sys.argv[0]
    self.h, self.help = None, None
    arg_str = self.flatten(sys.argv[1:])
    self.args = self.pairs(arg_str)
    self.set_vars()
    self.reflect()

  def __getattribute__(self, name) -> Any:
    """ Handle missing attributes and flags """
    try:
      attr = super().__getattribute__(name)
      return attr
    except AttributeError:
      print(f"\n\t ❌ ERROR: The program expected {name}, but didn't get a flag value for {name}!\n")
      sys.exit(1)

  def __str__(self) -> str:
    """ str representation """
    md = """

arglite

Hi! You're seeing this message because you used a help flag or
because there were no variable specified on the command line as
flags!

argparse is a CLI argument parser for the impatient

Usage

- Provide arbitary flags to a program at runtime
- Interpret flags with the argparse.parser object

    """
    return md

  def flatten(self, args: list = []) -> str:
    """ Flatten a list into a str """
    return " ".join(args)

  def pairs(self, args: str = "") -> list:
    """ Get each pair of args and values, blanks if no value """
    return re.findall(r"-{1,2}([^-][a-z]*(?:\s)?)([^-]*)", args)

  def typify(self, val: Any) -> Any:
    """ Cast as a data structure or other type if possible, else...meh """
    try:
      val = literal_eval(val)
    except:
      pass
    return val

  def set_help(self):
    """ Set the help flag response """
    del self.h
    del self.help
    print(self.__str__())
    self.display()

  def set_vars(self) -> None:
    """ Reflect each variable and value to instance """
    self.vars = []
    for arg, val in self.args:
      if not val: val = True
      if type(val) == str: val = val.strip()
      arg = arg.strip()
      if not arg == "h" and not arg == "help":
        self.vars.append(arg)
      setattr(self, arg, self.typify(val))
    if self.h or self.help or len(self.vars) == 0:
      self.set_help()

  def reflect(self) -> None:
    """ Gather information about expected variables """
    self.expected = []
    file = os.path.abspath(
      sys.argv[0]
    )
    code = Code(file)
    exp = f"{code.name}(\.parser)?\.([a-z0-9_])"
    regexp = re.compile(exp, re.I)
    for line in code.source:
      expected_vars = re.search(regexp, line)
      if expected_vars:
        self.expected.append(expected_vars.groups()[-1])

  def display(self) -> None:
    """ Display a table of all of the args parsed """
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
    if len(self.vars) > 0:
      console.print(table)


""" Create a simple instanced variable to run on exec """
parser = Parser()
