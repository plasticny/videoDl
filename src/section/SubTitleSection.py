from enum import Enum
from inquirer import prompt as inq_prompt, List as inq_List, Text as inq_Text, Checkbox as inq_Checkbox

from section.Section import Section
from service.YtDlpHelper import Opts

class SubTitleSection (Section):
  def run(self, opts:Opts = Opts()) -> Opts:
    return super().run(self.__main, opts=opts.copy())
  
  def __main(self, opts:Opts) -> Opts:
    # ask if write subtitle
    doWriteSub = inq_prompt([
      inq_List(
        'choice', message='Write the subtitle?', 
        choices=['Yes','No'], default='Yes'
      )
    ])['choice']
    doWriteSub = doWriteSub == 'Yes'

    # not write subtitle
    if not doWriteSub:
      opts.writeSubtitles = False
      return opts

    # if write subtitle, ask details
    ans = inq_prompt([
      inq_Text(
        'lang', message='Enter the language of subtitle', 
        default='en'
      ),
      inq_Checkbox(
        'writeMode', message='Choose the mode of writing subtitle (Space to select/deselect, Enter to confirm)',
        choices=['Embed', 'Burn'], default=['Embed', 'Burn']
      ),
      inq_List(
        'writeAutoSub', message='Wirte the auto-gen subtitle if could not find subtitle?', 
        choices=['Yes','No'], default='No'
      ),
    ])    
    opts.writeSubtitles = doWriteSub
    opts.subtitlesLang = ans['lang'] if len(ans['lang']) > 0 else 'en'
    opts.embedSubtitle = 'Embed' in ans['writeMode']
    opts.burnSubtitle = 'Burn' in ans['writeMode']
    opts.writeAutomaticSub = ans['writeAutoSub'] == 'Yes'

    # print warning if not doEmbedSub and not doBurnSub:
    if not opts.embedSubtitle and not opts.burnSubtitle:
      print('Warning: You choose not to embed or burn the subtitle to the video, so the subtitle will not be shown in the video.')

    return opts
