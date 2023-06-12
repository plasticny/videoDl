from section.Section import Section
from dlConfig import dlConfig
from commandUtils import runCommand

class DownloadSection (Section) :
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__download)
  
  def __download (self):
    config = self.config
    runCommand(paramCommands=[
      # url
      config.url,
      
      # format
      '-f',
         config.outputFormat,
      
      # subtitle
      '--embed-subs',
      # write auto subtitle
      config.doWriteAutoSubCommand(),
      # subtitle lang
      '--sub-langs',
        config.subLang,
      
      # output directory
      '-P',
         config.outputDir,
      
      # fixed param
      '--compat-options',
         'no-live-chat'
    ], printCommand=True)
