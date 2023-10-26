from enum import Enum

from section.Section import Section
from dlConfig import dlConfig
from service.commandUtils import runCommand, YT_EXEC
from service.YtDlpHelper import CommandConverter

class Message (Enum):
  DOWNLOAD_FAILED = 'Download failed'

class DownloadSection (Section) :
  # PARMAS:
  #   retry: int, the times of try to download again, default is 0
  def __init__(
      self, 
      title, 
      config:dlConfig, retry:int=0
    ):
    super().__init__(title)
    self.config = config
    self.retry = retry
    
  def run(self):
    return super().run(self.__download)
  
  # download video
  def __download (self):
    cc = CommandConverter(self.config)

    tryCnt = 0
    retc = None

    while retc != 0 and tryCnt <= self.retry:
      retc = runCommand(
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
      tryCnt += 1

    if retc != 0:
      raise Exception(Message.DOWNLOAD_FAILED.value)