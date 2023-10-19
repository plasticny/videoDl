from section.Section import Section
from dlConfig import dlConfig
from service.commandUtils import runCommand, YT_EXEC
from service.YtDlpHelper import CommandConverter

class ListFormatSection (Section):
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__listFormat)
  
  def __listFormat (self):
    doList = input('List available format?(N) ').upper()
    if doList=='N' or doList=='':
      return
    
    cc = CommandConverter(self.config)
    runCommand(
      execCommand=YT_EXEC,
      paramCommands=[
        cc.listFormat
      ]
    )