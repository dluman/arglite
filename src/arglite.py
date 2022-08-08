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
from .argument import Required
from .argument import Optional
from .argument import RequirementError

class Parser:

  def __init__(self):
    """ Entry point. """
    self.errors = [ ]
    self.file = sys.argv[0]
    self.h, self.help = None, None
    arg_str = self.flatten(sys.argv[1:])
    self.args = self.pairs(arg_str)
    self.required = Required()
    self.optional = Optional()
    self.set_vars()

    # Rattle off the error report
    for var in self.errors:
      print(f"✗ ERROR: The program required a value for {var}, but didn't receive one!")
    print(self.errors)
    # If there are required variable errors, DUCK OUT!
    if len(self.errors) > 0:
      exit(1)

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
    # If in neither of those places, see if the var
    # was required at at all
    try:
      if not self.expected[name]:
        raise RequirementError(name)
      if not name in self.errors:
        self.errors.append(name)
    # If RequirementError is raised, must be optional?
    except (KeyError, RequirementError):
      pass

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
    self.vars = { }
    obj = {
      True: self.required,
      False: self.optional
    }
    statuses = self.reflect()
    for arg, val in self.args:
      if not val: val = True
      if type(val) == str: val = val.strip()
      arg = arg.strip()
      setattr(obj[statuses[arg]], arg, self.typify(val))
      if not arg == "h" and not arg == "help":
        self.vars[arg] = getattr(obj[statuses[arg]], arg)
    if self.h or self.help or len(self.vars) == 0:
      self.set_help()

  def reflect(self) -> dict:
    """ Gather information about expected, required, and optional variables """
    self.expected = {
      "h": False,
      "help": False
    }
    file = os.path.abspath(
      sys.argv[0]
    )
    code = Code(file)
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

  def display(self) -> None:
    """ Display a table of all of the args parsed """
    table = Table(title="CLI flags")
    table.add_column("Variable name")
    table.add_column("Variable value")
    table.add_column("Variable type")
    table.add_column("Variable required")

    # All help flags never appear
    del self.expected["h"]
    del self.expected["help"]

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
    if len(list(self.vars.keys())) > 0:
      console.print(table)

# TODO: Write a system exit handler?

""" Create a simple instanced variable to run on exec """
parser = Parser()
