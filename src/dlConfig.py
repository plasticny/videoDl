from __future__ import annotations
from enum import Enum

class DefaultConfig (Enum):
  url = ''
  cookieFile = ''
  subLang = ''
  doWriteAutoSub = False
  outputFormat = ''
  outputDir = ''
  outputName = ''
  outputExt = ''
  h264 = False

class dlConfig:
  def __init__(self) -> None:
    # url
    self.url : str = None

    # cookies (for login)
    self.cookieFile = None

    # subtitle
    self.subLang : str = None
    self.doWriteAutoSub : bool = None

    # output setting
    self.outputFormat : str = None
    self.outputDir : str = None
    self.outputName : str = None
    self.outputExt : str = None
    self.h264 : bool = None

  @property
  def doWriteSub (self) -> bool:
    return self.subLang != None
  
  # giving another dlConfig c'
  # for every attribute of other is not None
  # copy the value of that attribute from another to self
  def overwriteConfigBy (self, other:dlConfig):
    for (attr, value) in other.__dict__.items():
      if value != None:
        setattr(self, attr, getattr(other, attr))

  # giving another dlConfig c'
  # for every attribute of self is None
  # copy the value of that attribute from another to self
  def fillConfigBy (self, other:dlConfig):
    for (attr, value) in self.__dict__.items():
      if value == None:
        setattr(self, attr, getattr(other, attr))
  