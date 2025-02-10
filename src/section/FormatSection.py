from __future__ import annotations

from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox # type: ignore
from inquirer.render.console import ConsoleRender # type: ignore
from colorama import Fore, Style
from typing import Union, Optional, Any, cast
from dataclasses import dataclass

from src.section.Section import Section
from src.section.DownloadSection import BundledFormat, DownloadOpt, TDownloadOpt
from src.service.MetaData import VideoMetaData
from src.service.autofill import get_lyd_media_autofill, get_lyd_format_option_autofill
from src.service.ytdlp import Ytdlp

from src.structs.video_info import MediaType

class FormatSection (Section):
  def run (self) -> str: # type: ignore
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input('Enter the format:(auto) ').lower()
    return 'mp4' if fo == '' or fo == 'auto' else fo


# ============== lazy format selection ============== #

# ==== Section return ==== #
@dataclass
class LazyFormatSectionRet:
  media: MediaType
  format_ls : list[Union[str, BundledFormat]]
  sort_ls: list[Optional[str]] # not a sorted list, but a list of Sorting Formats string for ytdlp

class LazyFormatSection (Section):
  """
    Select format with some default options
    instead entering format
  """
  def run (self, md_ls:list[VideoMetaData]) -> LazyFormatSectionRet: # type: ignore
    return super().run(self.__main, md_ls=md_ls)

  def __main(self, md_ls:list[VideoMetaData]) -> LazyFormatSectionRet:
    format_selector = LazyFormatSelector()

    media_option: MediaType = LazyMediaSelector().ask_media(md_ls)
    self.logger.info(f'Media option selected: {media_option}')
    
    format_option_res: LazyFormatSelector.SelectRes = format_selector.ask_format_option(md_ls, media_option)
    self.logger.info(f'Format option selected: {", ".join([k for k, v in format_option_res.__dict__.items() if v])}')

    format_ls: list[Union[str, BundledFormat]] = []
    sort_ls: list[Optional[str]] = []
    for md in md_ls:
      format_str = self._format_str(media_option, format_option_res)
      print(f'{Fore.CYAN}Checking option is available for [{md.title}]{Style.RESET_ALL}')
      while not self.check_format_str_available(md, format_str, format_option_res):
        # check if the format is available, if not ask to reselect the format option
        print(f'{Fore.YELLOW}The selected option is not available, please reselect.{Style.RESET_ALL}')
        reselected_option = format_selector.ask_format_option(
          [md], media_option, format_option_res
        )
        format_str = self._format_str(media_option, reselected_option)

      sort_str = self._sort_str(media_option, format_option_res)

      self.logger.info(f'[{md.title}] format_str: {format_str}')
      self.logger.info(f'[{md.title}] sort_str: {sort_str}')

      format_ls.append(format_str)
      sort_ls.append(sort_str)

    return LazyFormatSectionRet(media=media_option, format_ls=format_ls, sort_ls=sort_ls)

  def _format_str (self, media_option: MediaType, format_option: LazyFormatSelector.SelectRes) -> str:
    WIN_VCODEC_REGEX_FILTER = "[vcodec~='^(?!.*(hev|av01)).*$']"
    WIN_ACODEC_REGEX_FILTER = "[acodec~='^(?!.*opus).*$']"

    # both
    both_format_str = 'b'
    if format_option.WIN:
      if media_option == 'Video':
        both_format_str += WIN_VCODEC_REGEX_FILTER
      both_format_str += WIN_ACODEC_REGEX_FILTER

    # audio
    audio_format_str = 'ba'
    if format_option.WIN:
      audio_format_str += WIN_ACODEC_REGEX_FILTER
    if media_option == 'Audio':
      # download audio only,
      # or audio with video if no audio only format (audio will be extracted in DownloadSection)
      return f"{audio_format_str}/{both_format_str}"
    
    # video
    video_format_str = 'bv*'
    if format_option.WIN:
      video_format_str += WIN_VCODEC_REGEX_FILTER
    # download best video only, best audio only, and merge them
    # or download best format that has both video and audio
    return f'{video_format_str}+{audio_format_str}/{both_format_str}'
  
  def check_format_str_available (self, md: VideoMetaData, format_str: str, format_option: LazyFormatSelector.SelectRes) -> bool:
    if not format_option.WIN:
      return True
    
    opt = DownloadOpt(md.opts)
    opt.set_format(format_str)
    ytdlp_opt = cast(TDownloadOpt, DownloadOpt.to_ytdlp_dl_opt(opt))
    return Ytdlp(ytdlp_opt).check_format_available(md.url)
  
  def _sort_str (self, media_option: MediaType, format_option: LazyFormatSelector.SelectRes) -> Optional[str]:
    if not format_option.HRLS:
      return None
    if media_option == 'Audio':
      return 'asr,+size'
    return 'res,+size'
  
class LazyMediaSelector:
  """ select the media to be downloaded """
  def ask_media (self, md_ls:list[VideoMetaData]) -> MediaType:
    options: list[MediaType] = self._get_options(md_ls)
    
    if len(options) == 1:
      print('Only one media option available, select it automatically')
      print(f'Selected option: {Fore.CYAN}{options[0]}{Style.RESET_ALL}')
      return options[0]
    
    autofill = get_lyd_media_autofill()
    if autofill is not None:
      print('Media autofill found')
      print(f'Selected option: {Fore.CYAN}{options[autofill]}{Style.RESET_ALL}')
      return options[autofill]
    
    return inq_prompt([
      inq_List(
        'media_option', message=f'{Fore.CYAN}Select the media type{Style.RESET_ALL}', 
        choices=options, default=options[0]
      )
    ])['media_option'] # type: ignore
  
  def _get_options (self, md_ls:list[VideoMetaData]) -> list[MediaType]:
    options: list[MediaType] = []
    video_available = True
    audio_available = True
    
    for md in md_ls:
      if not video_available and not audio_available:
        break
      if len(md.formats['both']) != 0:
        continue
      video_available = video_available and len(md.formats['video']) != 0
      audio_available = audio_available and len(md.formats['audio']) != 0

    if video_available:
      options.append('Video')
    if audio_available:
      options.append('Audio')
      
    return options
  
class LazyFormatSelector:
  """ Some specific options for the download format """
  @dataclass
  class Option:
    name: str
    desc: str

  @dataclass
  class SelectRes:
    HRLS: bool = False
    WIN: bool = False

  OPTIONS: dict[str, Option] = {
    'HRLS': Option('Highest resolution lowest size', 'Download the highest resolution with the lowest size'),
    'WIN': Option('Make sure it plays on Windows', 'Avoid format that might not play on Windows player')
  }

  class QueryRender (ConsoleRender):
    def _print_options(self, render: Any):
      options = cast(list[tuple[LazyFormatSelector.Option, Any, Any]], render.get_options())
      for idx, (option, symbol, color) in enumerate(options):
        if idx == render.current:
          message = f"{option.name} ({option.desc})"
        else:
          message = f"{option.name}"
        self.print_line(" {color}{s} {m}{t.normal}", m=message, color=color, s=symbol) # type: ignore

  def ask_format_option(self, md_ls:list[VideoMetaData], media: MediaType, default: Optional[SelectRes] = None) -> SelectRes:
    """ Ask the user to select the option for choosing the format """
    default_provided = default is not None

    options = self._get_options(md_ls, media)
    if len(options) == 0:
      return LazyFormatSelector.SelectRes()
    
    autofill = get_lyd_format_option_autofill() if not default_provided else None
    if not default_provided:
      default = LazyFormatSelector.SelectRes()
    if autofill is not None:
      for option_key, selected in autofill.items():
        setattr(default, option_key, selected)

    default_choices: list[LazyFormatSelector.Option] = list(map(
      lambda option_key: self.OPTIONS[option_key],
      [option_key for option_key, selected in vars(default).items() if selected]
    ))
    selected_options: list[Optional] = inq_prompt( # type: ignore
      [
        inq_Checkbox(
          'format_option',
          message=f'{Fore.CYAN}Select format option(s){Style.RESET_ALL}',
          choices=options, default=default_choices
        )
      ],
      render=self.QueryRender()
    )['format_option'] # type: ignore

    res = LazyFormatSelector.SelectRes()
    for k in self.OPTIONS.keys():
      if self.OPTIONS[k] in selected_options:
        setattr(res, k, True)
    return res

  def _get_options(self, md_ls:list[VideoMetaData], media: MediaType) -> list[Option]:
    # no format option for audio
    if media == 'Audio':
      return []
    return [v for v in LazyFormatSelector.OPTIONS.values()]
# ============== lazy format selection ============== #
