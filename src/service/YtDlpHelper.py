from dlConfig import dlConfig, DefaultConfig

# ======== Convert Config Param to Command Param ======== #
class CommandConverter:
  def __init__ (self, config : dlConfig):
    self.config = config

  # url
  @property
  def url(self) -> str:
    if self.config.url == None:
      raise Exception('url is not set')
    return self.config.url
  
  # cookies
  @property
  def cookies(self) -> str:
    if self.config.cookieFile == None:
      raise Exception('cookieFile is not set')
    if self.config.cookieFile == DefaultConfig.cookieFile.value:
      return ''
    return f'--cookies {self.config.cookieFile}'

  # subtitle
  @property
  def embedSubs (self) -> str:
    return '--embed-subs' if self.config.subLang != None else ''
  @property
  def subLang (self) -> str:
    if self.config.subLang == None:
      raise Exception('subLang is not set')
    if self.config.subLang == DefaultConfig.subLang.value:
      return ''
    return f'--sub-lang {self.config.subLang}'
  @property
  def writeAutoSubs (self) -> str:
    if self.config.doWriteAutoSub == None:
      raise Exception('doWriteAutoSub is not set')
    return '--write-auto-subs' if self.config.doWriteSub and self.config.doWriteAutoSub else ''

  # output
  @property
  def outputName (self) -> str:
    if self.config.outputName == None:
      raise Exception('outputName is not set')
    if self.config.outputName == DefaultConfig.outputName.value:
      return ''
    return f'-o {self.config.outputName}.%(ext)s'
  @property
  def outputDir (self) -> str:
    if self.config.outputDir == None:
      raise Exception('outputDir is not set')
    if self.config.outputDir == DefaultConfig.outputDir.value:
      return ''
    return f'-P {self.config.outputDir}'
  @property
  def outputFormat (self) -> str:
    if self.config.outputFormat == None:
      raise Exception('outputFormat is not set')
    if self.config.outputFormat == DefaultConfig.outputFormat.value:
      return ''
    return f'-f {self.config.outputFormat}'
  
  # live chat
  @property
  def noLiveChat (self) -> str:
    return '--compat-options no-live-chat'
  
  # list info
  @property
  def listFormat (self) -> str:
    if self.config.url == None:
      raise Exception('url is not set')
    if self.config.url == DefaultConfig.url.value:
      return ''
    return f'--list-formats {self.url}'
  @property
  def listSubs (self) -> str:
    if self.config.url == None:
      raise Exception('url is not set')
    if self.config.url == DefaultConfig.url.value:
      return ''
    return f'--list-subs {self.url}'
