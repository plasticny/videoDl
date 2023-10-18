from section.Section import Section
from dlConfig import dlConfig
from service.commandUtils import runCommand, YT_EXEC

class ListSubtitleSection (Section):
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self) -> None:
    return super().run(self.__listSubTitle)
  
  def __listSubTitle (self) -> None:
    doList = input('List available subtitle?(N) ').upper()
    if doList=='N' or doList=='':
      return
    
    config = self.config
    runCommand(
      execCommand=YT_EXEC,
      paramCommands=[
        # login
        config.cookieFileCommand(),
        # list subtitle
        '--list-subs',
          config.url
      ]
    )
