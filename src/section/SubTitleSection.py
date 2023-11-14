from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox
from colorama import Fore, Style

from section.Section import Section
from service.YtDlpHelper import Opts
from service.MetaData import MetaData, VideoMetaData, Subtitle

class SubTitleSection (Section):
  def run(self, url, opts:Opts = Opts()) -> Opts:
    return super().run(self.__main, url=url, opts=opts.copy())
  
  def __main(self, url, opts:Opts) -> Opts:
    print('Finding subtitles...')
    md : VideoMetaData = MetaData.fetchMetaData(url, opts)

    if len(md.subtitles) == 0 and len(md.autoSubtitles) == 0:
      # if no subtitle, return
      print(f'{Fore.YELLOW}No subtitle available.{Style.RESET_ALL}')
      return opts
    else:
      print(f'{Fore.GREEN}Subtitles found{Style.RESET_ALL}.', end='')
      print(f'{Fore.YELLOW}{len(md.subtitles)}{Style.RESET_ALL} subtitle(s) and {Fore.YELLOW}{len(md.autoSubtitles)}{Style.RESET_ALL} auto-gen subtitle(s).')

    # not write subtitle
    if not self.selectWriteSub():
      opts.writeSubtitles = False
      return opts

    # if write subtitle, ask details
    (lang, isAuto) = self.selectSubtitle(md)
    (doEmbed, doBurn) = self.selectWriteMode()
    
    opts.subtitlesLang = lang
    opts.writeSubtitles = not isAuto
    opts.writeAutomaticSub = isAuto
    opts.embedSubtitle = doEmbed
    opts.burnSubtitle = doBurn

    # print warning if not doEmbedSub and not doBurnSub:
    if not opts.embedSubtitle and not opts.burnSubtitle:
      print(Fore.YELLOW)
      print('Warning: You do not choose any mode to write the subtitle, so the subtitle will not be shown in the video.')
      print(Style.RESET_ALL)

    return opts
  
  def selectWriteSub(self) -> bool:
    """
      Ask user to select whether to write subtitle
    """
    doWriteSub = inq_prompt([
      inq_List(
        'writeSub', message='Write the subtitle?', 
        choices=['Yes','No'], default='Yes'
      )
    ])['writeSub']
    return doWriteSub == 'Yes'
  
  def selectSubtitle(self, md : VideoMetaData) -> (str, bool):
    """
      Ask user to select subtitle from the list of subtitles

      Returns:
        (str, bool): (Code of the subtitle, is auto-gen subtitle)
    """
    ans : Subtitle = inq_prompt([
      inq_List('lang', message=f'Select a subtitle', choices=[*md.subtitles, *md.autoSubtitles])
    ])['lang']

    return (ans.code, ans.isAuto)
  
  def selectWriteMode(self) -> (bool, bool):
    """
      Ask user to select write mode

      Returns:
        (bool, bool): (doEmbedSub, doBurnSub)
    """
    ans = inq_prompt([
      inq_Checkbox(
        'writeMode', message='Choose the mode of writing subtitle (Space to select/deselect, Enter to confirm)',
        choices=['Embed', 'Burn'], default=['Embed', 'Burn']
      )
    ])['writeMode']

    return ('Embed' in ans, 'Burn' in ans)