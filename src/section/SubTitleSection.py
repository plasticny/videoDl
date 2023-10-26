from enum import Enum

from section.Section import Section

class VALUE(Enum):
  DEFAULT_IN_LANG = 'en'
  DEFAULT_IN_WRITE_AUTO_SUB = 'N'

class Message(Enum):
  ASK_LANG = f'Enter the language of subtitle:({VALUE.DEFAULT_IN_LANG.value}) '
  ASK_WRITE_AUTO_SUB = f'Wirte the auto subtitle?:({VALUE.DEFAULT_IN_WRITE_AUTO_SUB.value}) '

class SubTitleSection (Section):
  def run(self) -> (str, bool):
    return super().run(self.__main)
  
  def __main(self) -> (str, bool):
    # subtitle language
    lang = input(Message.ASK_LANG.value)
    lang = VALUE.DEFAULT_IN_LANG.value if lang == '' else lang
    
    # write auto subtitle
    doWriteAutoSub = input(Message.ASK_WRITE_AUTO_SUB.value).upper()
    doWriteAutoSub = doWriteAutoSub != VALUE.DEFAULT_IN_WRITE_AUTO_SUB.value
    
    return (lang, doWriteAutoSub)