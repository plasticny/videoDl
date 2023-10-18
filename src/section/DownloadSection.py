from section.Section import Section
from dlConfig import dlConfig
from service.commandUtils import runCommand, YT_EXEC

class DownloadSection (Section) :
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__download)
  
  def __download (self):
    config = self.config
    runCommand(
      execCommand=YT_EXEC,
      paramCommands=[
        # output file name
        config.outputNameCommand(),
        
        # output directory
        '-P',
          config.outputDir,
        
        # url
        config.url,

        # not download live chat
        '--compat-options no-live-chat',
        
        # format
        '-f',
          config.outputFormat,
        
        # subtitle
        '--embed-subs' if config.subLang is not None else '',
        # write auto subtitle
        config.doWriteAutoSubCommand(),
        # subtitle lang
        config.getSubLang(),
        
        # login
        config.cookieFileCommand()
      ], 
      printCommand=True
    )