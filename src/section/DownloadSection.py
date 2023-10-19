from section.Section import Section
from dlConfig import dlConfig
from service.commandUtils import runCommand, YT_EXEC
from service.YtDlpHelper import CommandConverter

class DownloadSection (Section) :
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__download)
  
  def __download (self):
    cc = CommandConverter(self.config)
    runCommand(
      execCommand=YT_EXEC,
      paramCommands=[
        # url
        cc.url,

        # output file name
        cc.outputName,
        # output directory
        cc.outputDir,
        # otuput format
        cc.outputFormat,
        
        # not download live chat
        cc.noLiveChat,
        
        # subtitle
        cc.embedSubs,
        # write auto subtitle
        cc.writeAutoSubs,
        # subtitle lang
        cc.subLang,
        
        # login
        cc.cookies
      ], 
      printCommand=True
    )