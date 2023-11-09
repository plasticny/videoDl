from enum import Enum

from yt_dlp import YoutubeDL

from section.Section import Section
from service.YtDlpHelper import Opts

class Message (Enum):
  DOWNLOAD_FAILED = 'Download failed'
  RETRY = 'Retry {} times'

class DownloadSection (Section) :
  # PARMAS:
  #   retry: int, the times of try to download again, default is 0    
  def run(self, url:str, opts:Opts=Opts(), retry:int=0):
    return super().run(self.__download, url=url, opts=opts.copy(), retry=retry)
  
  # download video
  def __download (self, url:str, opts:Opts, retry:int):
    opts = opts.copy().overwrites()

    tryCnt = 0
    while True:
      try:
        YoutubeDL(opts()).download([url])
        break
      except:
        tryCnt += 1
        if tryCnt > retry:
          raise Exception(Message.DOWNLOAD_FAILED.value)
        print(Message.RETRY.value.format(tryCnt))