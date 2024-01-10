from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import TypedDict
from typing_extensions import Self
from copy import deepcopy

class TOpt (TypedDict):
  pass
  
class IOpt (metaclass = ABCMeta):
  """
    Basic options for this tool\n
    "option" means values that can be set by user
  """
  @staticmethod
  def to_ytdlp_opt(obj : IOpt) -> TOpt:
    """ Convert the properties to a dict for ytdlp options """
    assert obj.url is not None
    return {}

  @abstractmethod
  def __init__(self) -> None:
    """ TODO: for child class, add options """
    self.url : str = None

  def copy(self) -> Self:
    return deepcopy(self)