from section.Section import Section
from dlConfig import dlConfig
from commandUtils import runCommand

class ListSubtitleSection (Section):
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__listSubTitle)
  
  def __listSubTitle (self):
    doList = input('List available subtitle?(N) ').upper()
    if doList=='N' or doList=='':
      return
    
    config = self.config
    runCommand(paramCommands=[
        # login
        config.cookieFileCommand(),
        # list subtitle
        '--list-subs',
            config.url
    ])