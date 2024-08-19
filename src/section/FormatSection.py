from __future__ import annotations

from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox
from colorama import Fore, Style
from typing import Union, Optional
from enum import Enum
from dataclasses import dataclass
from inquirer.render.console import ConsoleRender

from src.section.Section import Section
from src.section.DownloadSection import BundledFormat

from src.service.MetaData import VideoMetaData, TFormatVideo
from src.service.autofill import get_lyd_media_autofill, get_lyd_format_option_autofill

from src.structs.option import MediaType
  

class FormatSection (Section):
  def run(self) -> str:
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input('Enter the format:(auto) ').lower()
    return 'mp4' if fo == '' or fo == 'auto' else fo


# ============== lazy format selection ============== #
@dataclass
class LazyFormatSectionRet:
  media : MediaType
  format_ls : list[Union[str, BundledFormat]]

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

    format_ls : list[Union[str, BundledFormat]] = []
    for md in md_ls:
      audio_format = self._best_audio(md, format_option_res)

      # download audio only
      if media_option == LazyMediaType.AUDIO.value:
        if audio_format is None:
          raise ValueError('No audio available')
        selected_format = audio_format
      # video
      else:
        video_format = self._select_video_format(md, format_option_res)
        if video_format is None:
          raise ValueError('No video available')
        if audio_format is None:
          selected_format = video_format
        else:
          selected_format = BundledFormat(audio=audio_format, video=video_format)

      self.logger.info(
        '[{}] selected format: {}'.format(
          md.title,
          f'{selected_format.video} + {selected_format.audio}' if isinstance(selected_format, BundledFormat) else selected_format
        )
      )
      format_ls.append(selected_format)

    return LazyFormatSectionRet(media=media_option, format_ls=format_ls)

  def _best_audio (self, md:VideoMetaData, format_option_res: LazyFormatSelector.SelectRes) -> Optional[str]:
    if len(md.formats['audio']) != 0:
      for f in md.formats['audio']:
        if format_option_res.WIN and 'opus' in f['codec']:
          continue
        return f['format_id']
    
    if len(md.formats['both']) != 0:
      for f in md.formats['both']:
        if format_option_res.WIN and 'opus' in f['audio']['codec']:
          continue
        return f['audio']['format_id']

    return None
  
  def _select_video_format (self, md: VideoMetaData, format_option_res: LazyFormatSelector.SelectRes) -> Optional[str]:
    """ Select the video format with the best resolution and fulfill the format option """
    # format is supposed to be sorted by quality first and size second
    selected_format: Optional[TFormatVideo] = None
    for f in md.formats['video']:
      # avoid format that might not play on Windows player
      if format_option_res.WIN and ('hev' in f['codec'] or 'av01' in f['codec']):
        continue

      # first format
      if selected_format is None:
        selected_format = f
      # highest resolution lowest size
      elif format_option_res.HRLS and f['width'] == selected_format['width'] and f['height'] == selected_format['height']:
        selected_format = f
      else:
        break

    if selected_format is None:
      return None
    return selected_format['format_id']

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
