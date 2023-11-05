from enum import Enum

from section.Section import Section
from service.YtDlpHelper import Opts

class VALUE(Enum):
  IN_AUTO = 'auto'
  IN_EMPTY = ''
  OUT_DEFAULT = 'mp4'

class Message(Enum):
  ASK_FORMAT = f'Enter the format:({VALUE.IN_AUTO.value}) '

class FormatSection (Section):
  def run(self, opts:Opts = Opts()) -> Opts:
    return super().run(self.__main, opts=opts.copy())
  
  def __main(self, opts:Opts) -> Opts:
    fo = input(Message.ASK_FORMAT.value).lower()
    if fo == VALUE.IN_AUTO.value or fo == VALUE.IN_EMPTY.value:
      opts.format(VALUE.OUT_DEFAULT.value)
    else:
      opts.format(fo)
    return opts