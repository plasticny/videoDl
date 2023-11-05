from yt_dlp import YoutubeDL

from enum import Enum

from section.Section import Section
from service.YtDlpHelper import Opts

class VALUE(Enum):
  IN_NOT_LIST = 'N'
  IN_EMPTY = ''

class Message(Enum):
  ASK_DO_LIST = 'List available format?(N) '

class ListFormatSection (Section):    
  def run(self, url:str, opts:Opts=Opts()) -> None:
    return super().run(self.__listFormat, url=url, opts=opts.copy())
  
  def __listFormat (self, url:str, opts:Opts):
    doList = input(Message.ASK_DO_LIST.value).upper()
    if doList==VALUE.IN_NOT_LIST.value or doList==VALUE.IN_EMPTY.value:
      return

    YoutubeDL(
      params=opts.skip_download().listFormats()()
    ).download([url])