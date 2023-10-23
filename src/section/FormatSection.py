from enum import Enum

from section.Section import Section

class Message(Enum):
  ASK_FORMAT = 'Enter the format:(auto) '

class FormatSection (Section):
  def run(self) -> str:
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input(Message.ASK_FORMAT.value).lower()
    return 'mp4' if fo == 'auto' or fo == '' else fo
