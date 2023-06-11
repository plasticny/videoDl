from __future__ import annotations

class dlConfig:
  def __init__(self) -> None:
    
    self.url = None
    self.cookieFile = None
    self.subLang = None
    self.doWriteAutoSub = None
    self.outputFormat = None
    self.outputDir = None
  
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
  