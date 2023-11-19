from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox
from colorama import Fore, Style

from section.Section import Section
from service.YtDlpHelper import Opts
from service.MetaData import MetaData, VideoMetaData
from service.structs import Subtitle

class SubTitleSection (Section):
  def run(self, md:MetaData, opts:Opts = Opts()) -> Opts:
    return super().run(self.__main, md=md, opts=opts.copy())
  
  def __main(self, md:MetaData, opts:Opts) -> Opts:
    if md.isPlaylist():
      print(f'{Fore.YELLOW}Write subtitle into playlist video is not supported currently.{Style.RESET_ALL}')
      opts.writeSubtitles = False
      return opts

    if len(md.subtitles) == 0 and len(md.autoSubtitles) == 0:
      # if no subtitle, return
      print(f'{Fore.YELLOW}No subtitle available.{Style.RESET_ALL}')
      opts.writeSubtitles = False
      return opts
    else:
      print(f'{Fore.GREEN}Subtitles found{Style.RESET_ALL}.', end='')
      print(f'{Fore.YELLOW}{len(md.subtitles)}{Style.RESET_ALL} subtitle(s) and {Fore.YELLOW}{len(md.autoSubtitles)}{Style.RESET_ALL} auto-gen subtitle(s).')

    # not write subtitle
    if not self.selectWriteSub():
      opts.writeSubtitles = False
      return opts
    
    # if write subtitle, ask details
    (lang, isAuto, doEmbed, doBurn) = self.selectDetails(md)
    opts.subtitlesLang = lang
    opts.writeSubtitles = not isAuto
    opts.writeAutomaticSub = isAuto
    opts.embedSubtitle = doEmbed
    opts.burnSubtitle = doBurn

    # print warning if not doEmbedSub and not doBurnSub:
    if not opts.embedSubtitle and not opts.burnSubtitle:
      print(Fore.YELLOW)
      print('Warning: You did not choose any mode to write the subtitle, so the subtitle will not be shown in the video.')
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
  
  def selectDetails(self, md : VideoMetaData) -> (str, bool, bool, bool):
    """
      Select subtitle language and write mode

      Returns:
        (Code of the subtitle, is auto-gen subtitle, do embed sub, do burn sub)
    """
    ans = inq_prompt([
      inq_List('lang', message=f'Select a subtitle', choices=[*md.subtitles, *md.autoSubtitles]),
      inq_Checkbox(
        'writeMode', message='Choose the mode of writing subtitle (Space to select/deselect, Enter to confirm)',
        choices=['Embed', 'Burn'], default=['Embed', 'Burn']
      )
    ])

    sub : Subtitle = ans['lang']
    mode : list[str] = ans['writeMode']

    return (sub.code, sub.isAuto, 'Embed' in mode, 'Burn' in mode)