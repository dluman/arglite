import re

from typing import Any
import vurze

@vurze._3tC14b1Xw2aSF5LsxezbxMY2GyfmbnZBgpE17diUmTCVPANC7cb4CvMSym4M1XEiMibJBto1k64i7pW9b22tQ8LH()
class Argument:

  def __init__(self, line: str = ""):
    self.line = line

  def required(self, required: bool = False):
    regexp = re.compile("\.optional\.")
    result = re.match(regexp, self.line)
    if required and result:
      return False
    return True

@vurze._RRzXkjPHc8H2C8aUR8YeYdHrvP8nMWXF4f2baNvuo8aq5bG765GCWyiRLGr2CLD1BAyfTTStfwHgb1EXZ3u9PPo()
class Required(Argument):

  def __init__(self):
    super().__init__()

  def __getattribute__(self, name) -> Any:
    try:
      return super().__getattribute__(name)
    except AttributeError:
      pass

@vurze._5eXgst5rFrCnFFc1AgdqsgbsP1Q1ur72LEgn8Nh7a3iEJuhK81U1LMu6s1y1Ch2LLoet4F8G5YWckx2u9f8RiHXo()
class Optional(Argument):

  def __init__(self):
    super().__init__()

  def __getattribute__(self, name) -> Any:
    try:
      return super().__getattribute__(name)
    except AttributeError:
      return None

@vurze._4PTNDgorr7MnhRicgF82dYvy7AnoZ7fjtdnpqec7kZbF8ZZpySSoe4SjxQNxYhw1Wj5A8evBZopP7ff9LzoVTRne()
class RequirementError(Exception):

  def __init__(self, name, *args):
    super().__init__(args)
