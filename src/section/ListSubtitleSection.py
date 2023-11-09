from yt_dlp import YoutubeDL

from enum import Enum

from section.Section import Section
from service.YtDlpHelper import Opts

class VALUE(Enum):
  IN_NOT_LIST = 'N'
  IN_EMPTY = ''

class Message(Enum):
  ASK_DO_LIST = 'List available subtitles?(N) '

class ListSubtitleSection (Section):
  # opts is necessary for the cookie
  def run(self, url:str, opts:Opts=Opts()) -> None:
    return super().run(self.__listSubTitle, url=url, opts=opts.copy())
  
  def __listSubTitle (self, url:str, opts:Opts) -> None:
    doList = input(Message.ASK_DO_LIST.value).upper()
    if doList==VALUE.IN_NOT_LIST.value or doList==VALUE.IN_EMPTY.value:
      return
    
    YoutubeDL(
      params=opts.skip_download().listSubtitle()()
    ).download([url])