from __future__ import annotations
from service.YtFetcher import getYtSongTitle

class dlConfig:
  def __init__(self) -> None:
    
    self.url : str = None
    self.cookieFile = None
    self.subLang : str = None
    self.doWriteAutoSub : bool = None
    self.outputFormat : str = None
    self.outputDir = None
    self.outputName : str = None
    self.outputExt : str = None
    self.h264 : bool = None
  
  def cookieFileCommand (self) -> str:
    return f'--cookies {self.cookieFile}' if self.cookieFile != None else ''
  
  def doWriteAutoSubCommand (self) -> str:
    return '--write-auto-subs' if self.doWriteAutoSub else ''
  
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
  
  # ###### #
  # getter #
  
  def outputNameCommand (self) -> str:
    if self.outputName == None:
      return ''
    return f'-o {self.outputName}.%(ext)s'
  
  def getFileName (self) -> str:
    if self.outputName == None:
      self.autoSetFileName()
    return self.outputName

  def getSubLang (self) -> str:
    if self.subLang == None:
      return ''
    return f'--sub-langs {self.subLang}'


  # ###### #
  # setter #

  def autoSetFileName (self) -> None:
    name = f"{getYtSongTitle(self.url)}[{self.url.split('=')[-1]}]"
    name = name.replace(' ', '_').replace('&','_')
    self.outputName = name
  