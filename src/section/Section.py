import sys
from enum import Enum
from typing import Callable, Optional, Any

from src.service.logger import Logger

class HeaderType(Enum):
  HEADER = 1
  SUB_HEADER = 2

class Section:
  def __init__(
      self, title:str='',
      doShowHeader:bool=True, doShowFooter:bool=True,
      headerType:HeaderType=HeaderType.HEADER
    ):
    self.title = title
    self.doShowHeader = doShowHeader
    self.doShowFooter = doShowFooter

    self.headerType = headerType
    
    self.logger = Logger()
    
  @property
  def header (self):
    return f"================= {self.title} ================="
  
  @property
  def subHeader (self):
    return f"## {self.title}"
  
  @property
  def footer (self):
    return ''
    
  def run (self, bodyFunc: Optional[Callable[..., Any]] = None, **kwargs: ...) -> Any:
    sys.stdout.flush()
        
    # header
    if self.doShowHeader:
      if self.headerType == HeaderType.HEADER:
        print(self.header)
      elif self.headerType == HeaderType.SUB_HEADER:
        print(self.subHeader)

    # body
    if bodyFunc is not None:
      result = bodyFunc(**kwargs)
    else:
      result = None

    # footer
    if self.doShowFooter:
      print(self.footer)
    
    return result
  