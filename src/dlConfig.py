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

class dlConfig:
  def __init__(
      self,
      url:str = None,
      cookieFile:str = None,
      subLang:str = None, doWriteAutoSub:bool = None,
      outputFormat:str = None, outputDir:str = None, outputName:str = None, outputExt:str = None,
    ) -> None:
    # url
    self.url:str = url

    # cookies (for login)
    self.cookieFile:str = cookieFile

    # subtitle
    self.subLang:str = subLang
    self.doWriteAutoSub:bool = doWriteAutoSub

    # output setting
    self.outputFormat:str = outputFormat
    self.outputDir:str = outputDir
    self.outputName:str = outputName
    self.outputExt:str = outputExt

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

  # set all attribute to default value
  def default(self):
    for (attr, value) in DefaultConfig.__members__.items():
      setattr(self, attr, value.value)