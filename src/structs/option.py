from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import TypedDict, Literal
from typing_extensions import Self
from copy import deepcopy

# download meida type options
MediaType = Literal['Video', 'Audio']

class TOpt (TypedDict):
  cookiefile : str
  
class Opt (metaclass = ABCMeta):
  """
    Basic options for this tool\n
  """
  @staticmethod
  def to_ytdlp_opt(obj : Opt) -> TOpt:
    """ Convert the properties to a dict for ytdlp options """
    assert obj.url is not None
    return {
      'cookiefile': obj.cookie_file_path,
      'login_browser': obj.login_browser
    }

  def __init__ (self, other : Opt = None) -> None:
    self.url : str = None
    self.cookie_file_path : str = None
    self.login_browser : str = None

    if other is not None:
      assert isinstance(other, Opt)
      self.url = other.url
      self.cookie_file_path = other.cookie_file_path
      self.login_browser = other.login_browser

  def copy(self) -> Self:
    return deepcopy(self)