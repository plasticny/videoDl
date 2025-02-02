from __future__ import annotations

from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox
from colorama import Fore, Style
from typing import Union, Optional
from enum import Enum
from dataclasses import dataclass
from inquirer.render.console import ConsoleRender

from src.section.Section import Section
from src.section.DownloadSection import BundledFormat

from src.service.MetaData import VideoMetaData
from src.service.autofill import get_lyd_media_autofill, get_lyd_format_option_autofill

from src.structs.option import MediaType
  

class FormatSection (Section):
  def run(self) -> str:
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input('Enter the format:(auto) ').lower()
    return 'mp4' if fo == '' or fo == 'auto' else fo


# ============== lazy format selection ============== #

# ==== Section return ==== #
@dataclass
class LazyFormatSectionRet:
  media : MediaType
  format_ls : list[Union[str, BundledFormat]]
  sort_ls: list[Optional[str]] # not a sorted list, but a list of Sorting Formats string for ytdlp

class LazyMediaType (Enum):
  VIDEO = 'Video'
  AUDIO = 'Audio'

class LazyFormatSection (Section):
  """
    Select format with some default options
    instead entering format
  """
  def run(self, md_ls:list[VideoMetaData]) -> LazyFormatSectionRet:
    return super().run(self.__main, md_ls=md_ls)

  def __main(self, md_ls:list[VideoMetaData]) -> list[Union[str, BundledFormat]]:
    media_option : str = LazyMediaSelector()._ask_media(md_ls)
    self.logger.info(f'Media option selected: {media_option}')
    
    format_option_res: LazyFormatSelector.SelectRes = LazyFormatSelector()._ask_format_option(md_ls, media_option)
    self.logger.info(f'Format option selected: {", ".join([k for k, v in format_option_res.__dict__.items() if v])}')

    format_ls: list[Union[str, BundledFormat]] = []
    sort_ls: list[Optional[str]] = []
    for md in md_ls:
      format_str = self._format_str(media_option, format_option_res)
      sort_str = self._sort_str(media_option, format_option_res)

      self.logger.info(f'[{md.title}] format_str: {format_str}')
      self.logger.info(f'[{md.title}] sort_str: {sort_str}')

      format_ls.append(format_str)
      sort_ls.append(sort_str)

    return LazyFormatSectionRet(media=media_option, format_ls=format_ls, sort_ls=sort_ls)

  def _format_str (self, media_option: str, format_option: LazyFormatSelector.SelectRes) -> str:
    WIN_VCODEC_REGEX_FILTER = "[vcodec~='^(?!.*(hev|av01)).*$']"
    WIN_ACODEC_REGEX_FILTER = "[acodec~='^(?!.*opus).*$']"

    # both
    both_format_str = 'b'
    if format_option.WIN:
      if media_option == LazyMediaType.VIDEO.value:
        both_format_str += WIN_VCODEC_REGEX_FILTER
      both_format_str += WIN_ACODEC_REGEX_FILTER

    # audio
    audio_format_str = 'ba'
    if format_option.WIN:
      audio_format_str += WIN_ACODEC_REGEX_FILTER
    if media_option == LazyMediaType.AUDIO.value:
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
  
  def _sort_str (self, media_option: str, format_option: LazyFormatSelector.SelectRes) -> Optional[str]:
    if not format_option.HRLS:
      return None
    if media_option == LazyMediaType.AUDIO.value:
      return 'asr,+size'
    return 'res,+size'

class LazyMediaSelector:
  """ select the media to be downloaded """
  def _ask_media (self, md_ls:list[VideoMetaData]) -> str:
    options = self._get_options(md_ls)
    
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
    ])['media_option']
  
  def _get_options (self, md_ls:list[VideoMetaData]) -> list[str]:
    options = []
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
      options.append(LazyMediaType.VIDEO.value)
    if audio_available:
      options.append(LazyMediaType.AUDIO.value)
      
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
    def _print_options(self, render):
      for idx, (option, symbol, color) in enumerate(render.get_options()):
        if idx == render.current:
          message = f"{option.name} ({option.desc})"
        else:
          message = f"{option.name}"
        self.print_line(" {color}{s} {m}{t.normal}", m=message, color=color, s=symbol)

  def _ask_format_option(self, md_ls:list[VideoMetaData], media : str) -> SelectRes:
    """ Ask the user to select the option for choosing the format """

    # no specific format option for audio
    if media == LazyMediaType.AUDIO.value:
      return LazyFormatSelector.SelectRes()
    
    options = self._get_options(md_ls)
    if len(options) == 0:
      return LazyFormatSelector.SelectRes()
    
    default = []
    autofill = get_lyd_format_option_autofill()
    if autofill is not None:
      default = [self.OPTIONS[k] for k, v in autofill.items() if v]

    selected_options = inq_prompt(
      [inq_Checkbox('format_option', message=f'{Fore.CYAN}Select format option(s){Style.RESET_ALL}', choices=options, default=default)],
      render=self.QueryRender()
    )['format_option']

    res = LazyFormatSelector.SelectRes()
    for k in self.OPTIONS.keys():
      if self.OPTIONS[k] in selected_options:
        setattr(res, k, True)
    return res
                      
  def _get_options(self, md_ls:list[VideoMetaData]) -> list[Option]:
    return [ v for v in LazyFormatSelector.OPTIONS.values() ]
# ============== lazy format selection ============== #
