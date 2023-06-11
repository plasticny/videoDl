from section.Section import Section
from dlConfig import dlConfig
from commandUtils import runCommand

class ListFormatSection (Section):
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__listFormat)
  
  def __listFormat (self):
    config = self.config
    runCommand(paramCommands=[
        # login
        config.cookieFileCommand(),
        # list format
        '--list-formats',
            config.url
    ])