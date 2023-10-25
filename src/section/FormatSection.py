from enum import Enum

from section.Section import Section

class VALUE(Enum):
  IN_AUTO = 'auto'
  IN_EMPTY = ''
  OUT_DEFAULT = 'mp4'

class Message(Enum):
  ASK_FORMAT = f'Enter the format:({VALUE.IN_AUTO.value}) '

class FormatSection (Section):
  def run(self) -> str:
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input(Message.ASK_FORMAT.value).lower()
    if fo == VALUE.IN_AUTO.value or fo == VALUE.IN_EMPTY.value:
      return VALUE.OUT_DEFAULT.value
    return fo