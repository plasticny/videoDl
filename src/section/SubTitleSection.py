from enum import Enum

from section.Section import Section

class Message(Enum):
  ASK_LANG = 'Enter the language of subtitle:(en) '
  ASK_WRITE_AUTO_SUB = 'Wirte the auto subtitle?:(N) '

class SubTitleSection (Section):
  def run(self) -> (str, bool):
    return super().run(self.__main)
  
  def __main(self) -> (str, bool):
    # subtitle language
    lang = input(Message.ASK_LANG.value)
    lang = 'en' if lang == '' else lang
    
    # write auto subtitle
    doWriteAutoSub = input(Message.ASK_WRITE_AUTO_SUB.value).upper()
    doWriteAutoSub = doWriteAutoSub != ''
    
    return (lang, doWriteAutoSub)