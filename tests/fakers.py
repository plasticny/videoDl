class fake_CommandConverter:
  def __init__(
      self, config,
      doListFormat:bool=False,
      doListSubs:bool=False,
    ) -> None:
    self.doListFormat = doListFormat
    self.doListSubs = doListSubs
    pass

  @property
  def url(self) -> str:
    return 'url'
  
  @property
  def outputName(self) -> str:
    return 'output name'
  @property
  def outputDir(self) -> str:
    return 'output dir'
  @property
  def outputFormat(self) -> str:
    return 'output format'

  @property
  def listFormat(self) -> str:
    if not(self.doListFormat):
      raise AttributeError()
    return 'list format'
  @property
  def listSubs(self) -> str:
    if not(self.doListSubs):
      raise AttributeError()
    return 'list subs'
  
  @property
  def noLiveChat(self) -> str:
    return 'no live chat'
  
  @property
  def embedSubs(self) -> str:
    return 'embed subs'
  @property
  def writeAutoSubs(self) -> str:
    return 'write auto subs'
  @property
  def subLang(self) -> str:
    return 'sub lang'
  
  @property
  def cookies(self) -> str:
    return 'cookies'

def fake_runCommand(execCommand, paramCommands:list=[], printCommand:bool=False):
  pass
