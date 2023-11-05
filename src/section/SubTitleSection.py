from enum import Enum

from section.Section import Section
from service.YtDlpHelper import Opts

class VALUE(Enum):
  DEFAULT_DO_WRITE_SUB = 'Y'
  DEFAULT_IN_LANG = 'en'
  DEFAULT_IN_WRITE_AUTO_SUB = 'N'

class Message(Enum):
  ASK_DO_WRITE = f'Write the subtitle?({VALUE.DEFAULT_DO_WRITE_SUB.value}) '
  ASK_LANG = f'Enter the language of subtitle:({VALUE.DEFAULT_IN_LANG.value}) '
  ASK_WRITE_AUTO_SUB = f'Wirte the auto subtitle?:({VALUE.DEFAULT_IN_WRITE_AUTO_SUB.value}) '

class SubTitleSection (Section):
  def run(self, opts:Opts = Opts()) -> Opts:
    return super().run(self.__main, opts=opts)
  
  def __main(self, opts:Opts) -> Opts:
    # do write subtitle
    doWriteSub = input(Message.ASK_DO_WRITE.value).upper()
    doWriteSub = doWriteSub == VALUE.DEFAULT_DO_WRITE_SUB.value or doWriteSub == ''

    if doWriteSub:
      # subtitle language
      lang = input(Message.ASK_LANG.value)
      lang = VALUE.DEFAULT_IN_LANG.value if lang == '' else lang
      
      # write auto subtitle
      doWriteAutoSub = input(Message.ASK_WRITE_AUTO_SUB.value).upper()
      doWriteAutoSub = doWriteAutoSub != VALUE.DEFAULT_IN_WRITE_AUTO_SUB.value
    else:
      lang = None
      doWriteAutoSub = None
    
    return opts.writeSubtitles(doWriteSub).subtitlesLang(lang).writeAutomaticSub(doWriteAutoSub)
