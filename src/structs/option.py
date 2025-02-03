from __future__ import annotations
from abc import ABCMeta
from typing import TypedDict, Optional
from typing_extensions import Self
from copy import deepcopy

class TOpt (TypedDict):
  cookiefile: Optional[str]
  login_browser: Optional[str]
  
class Opt (metaclass = ABCMeta):
  """
    Basic options for this tool\n
  """
  @staticmethod
  def to_ytdlp_opt(obj : Opt) -> TOpt:
    """ Convert the properties to a dict for ytdlp options """
    assert obj.url is not None, 'opt.url is required'
    return {
      'cookiefile': obj.cookie_file_path,
      'login_browser': obj.login_browser
    }

  def __init__ (self, other: Optional[Opt] = None) -> None:
    self.url: Optional[str] = None
    self.cookie_file_path: Optional[str] = None
    self.login_browser: Optional[str] = None

    if other is not None:
      assert isinstance(other, Opt)
      self.url = other.url
      self.cookie_file_path = other.cookie_file_path
      self.login_browser = other.login_browser

  def copy(self) -> Self:
    return deepcopy(self)
