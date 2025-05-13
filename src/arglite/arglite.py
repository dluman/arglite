import re
import os
import sys
import signal
import inspect
import importlib

from typing import Any
from ast import literal_eval

from rich import print
from rich.table import Table
from rich.console import Console
from rich.markdown import Markdown

from .code import Code
from .argument import Required
from .argument import Optional
from .argument import RequirementError

class Parser:

  def __init__(self):
    """ Entry point. """
    self.file = self.caller()
    self.h, self.help = None, None
    arg_str = self.flatten(sys.argv[1:])
    self.args = self.pairs(arg_str)
    self.required = Required()
    self.optional = Optional()
    self.set_vars()
    self.get_errors()

    for error in self.errors:
      print(f"✗ ERROR: A value was expected for {error}, but not was provided as a flag")
      sys.exit(1)

    if self.optional.h or self.optional.help:
      self.set_help()

  def __getattribute__(self, name) -> Any:
    """ Handle missing attributes and flags """
    # Try to get the variable from self first
    try:
      return super().__getattribute__(name)
    except AttributeError:
      # If not there, check the self.required set
      if hasattr(self.required, name):
        attr = self.required.__getattribute__(name)
        if attr: return attr

  def __str__(self) -> str:
    """ str representation """
    md = """
arglite

argparse is a CLI argument parser for the impatient

Hi! You're seeing this message because you used a help flag or
because there were no variables specified on the command line as
flags!

Usage

- Provide arbitary flags to a program at runtime
- Interpret flags with the argparse.parser object
    """
    return md

  def caller(self) -> str:
    stack = inspect.stack()
    for frame in stack:
      if frame.function == "<module>":
        if os.path.dirname(frame.filename) != os.path.dirname(__file__):
            return frame.filename

  def flatten(self, args: list = []) -> str:
    """ Flatten a list into a str """
    return " ".join(args)

  def pairs(self, args: str = "") -> list:
    """ Get each pair of args and values, blanks if no value """
    return re.findall(r"((-{1,2}[a-z\_0-9]+)(\s)?)([a-zA-Z\_0-9\.\:\/\s]+|\"[a-zA-Z0-9\s\._]+\"|\{.*\}|\[.*\])?",args)

  def typify(self, val: Any) -> Any:
    """ Cast as a data structure or other type if possible, else...meh """
    try:
      val = literal_eval(val)
    except:
      pass
    return val

  def set_help(self):
    """ Set the help flag response """
    print(self.__str__())
    self.display()

  def set_vars(self) -> None:
    """ Reflect each variable and value to instance """
    self.vars = { }
    obj = {
      True: self.required,
      False: self.optional
    }
    statuses = self.reflect()
    for arg, flag, sep, val in self.args:
      if not val: val = True
      if type(val) == str: val = val.strip()
      arg = arg.strip().replace("-","")
      try:
        setattr(obj[statuses[arg]], arg, self.typify(val))
      except KeyError:
        print(f"✗ ERROR: A value was provided for {arg}, but the program doesn't call for it")
      if not arg == "h" and not arg == "help":
        try:
          self.vars[arg] = getattr(obj[statuses[arg]], arg)
        except KeyError: pass

  def reflect(self) -> dict:
    """ Gather information about expected, required, and optional variables """
    self.expected = {
      "h": False,
      "help": False
    }
    code = Code(self.file)
    exp = f"{code.name}(\.parser)?(\.[a-z0-9_]+)?\.([a-z0-9_]+)"
    regexp = re.compile(exp, re.I)
    for line in code.source:
      while True:
        expected_vars = re.search(regexp, line)
        if not expected_vars: break
        if expected_vars:
          var = expected_vars.groups()[-1]
          req = expected_vars.groups()[-2]
          self.expected[var] = False if req == ".optional" else True
          line = line[expected_vars.end():]
    return self.expected

  def get_errors(self) -> None:
    self.errors = [ ]
    for var in self.expected:
      if self.expected[var] and not var in dir(self.required):
        self.errors.append(var)

  def display(self) -> None:
    """ Display a table of all of the args parsed """
    table = Table(title="CLI flags")
    table.add_column("Variable name")
    table.add_column("Variable value")
    table.add_column("Variable type")
    table.add_column("Variable required")

    helps = ["h", "help"]

    for help in helps:
      try:
        del self.expected[help]
      except:
        pass

    for var in list(self.expected.keys()):
      # Callables shouldn't appear either
      if hasattr(self, var):
        if callable(getattr(self, var)):
          continue
      # The real business
      if self.expected[var]:
        try:
          val = getattr(self.required, var)
        except: pass
      else:
        try:
          val = getattr(self.optional, var)
        except: pass
      table.add_row(
        var,
        str(val),
        type(val).__name__,
        "🗸" if self.expected[var] else "✗"
      )

    console = Console()
    console.print(table)

""" Create a simple instanced variable to run on exec """
parser = Parser()
