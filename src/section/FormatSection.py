from inquirer import prompt as inq_prompt, List as inq_List
from colorama import Fore, Style
from typing import Union, Literal
from enum import Enum
from dataclasses import dataclass

from src.section.Section import Section
from src.section.DownloadSection import BundledFormat

from src.service.MetaData import VideoMetaData
from src.service.autofill import get_lyd_format_autofill, get_lyd_media_autofill
  

class FormatSection (Section):
  def run(self) -> str:
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input('Enter the format:(auto) ').lower()
    return 'mp4' if fo == '' or fo == 'auto' else fo


# ============== lazy format selection ============== #
@dataclass
class LazyFormatSectionRet:
  media : Literal['Video', 'Audio']
  format_ls : list[Union[str, BundledFormat]]

class LazyMediaType (Enum):
  VIDEO = 'Video'
  AUDIO = 'Audio'

class LazyFormatType (Enum):
  BEST_QUALITY = 'Best quality' # download best quality
  BEST_QUALITY_LOW_SIZE = 'Best quality lowest size' # download the lowest size of the best quality
  QUALITY_EFFICIENT = 'Quality-efficient balance' # download best quality, but avoid video editing

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
    
    format_option : str = LazyFormatSelector()._ask_format_option(md_ls, media_option)
    self.logger.info(f'Format option selected: {format_option}')
  
    format_ls : list[Union[str, BundledFormat]] = []
    for md in md_ls:
      # audio
      if media_option == LazyMediaType.AUDIO.value:
        selected_format = self._best_audio(md)
      # video
      elif format_option == LazyFormatType.QUALITY_EFFICIENT.value:
        selected_format = self._quality_efficient(md)
      elif format_option in [LazyFormatType.BEST_QUALITY.value, LazyFormatType.BEST_QUALITY_LOW_SIZE.value]:
        selected_format = self._best_quality(md, format_option)
      else:
        raise ValueError(f'Invalid format option: {format_option}')

      self.logger.info(
        '[{}] selected format: {}'.format(
          md.title,
          f'{selected_format.video} + {selected_format.audio}' if isinstance(selected_format, BundledFormat) else selected_format
        )
      )
      format_ls.append(selected_format)

    return LazyFormatSectionRet(media=media_option, format_ls=format_ls)

  def _best_audio (self, md:VideoMetaData) -> str:
    if len(md.formats['audio']) != 0:
      return md.formats['audio'][0]['format_id']
    elif len(md.formats['both']) != 0:
      return md.formats['both'][0]['audio']['format_id']
    else:
      raise ValueError('No audio available')
  
  def _quality_efficient (self, md:VideoMetaData) -> Union[str, BundledFormat]:
    if len(md.formats['both']) > 0:
      return md.formats['both'][0]['format_id']
    elif len(md.formats['audio']) == 0:
      return md.formats['video'][0]['format_id']
    else:
      v = md.formats['video'][0]['format_id']
      a = md.formats['audio'][0]['format_id']
      return BundledFormat(video = v, audio = a)
  
  def _best_quality (self, md:VideoMetaData, format_option : str) -> Union[str, BundledFormat]:
    """ Best quality or best quality lowest size """
    # best quality and best quality smallest size
    video_format = md.formats['video'][0]
    if format_option == LazyFormatType.BEST_QUALITY_LOW_SIZE.value:
      # select a format with same resolution but smallest size
      # format is supposed to be sorted by quality first and size second
      for f in md.formats['video'][1:]:
        if f['width'] == video_format['width'] and f['height'] == video_format['height']:
          video_format = f
        else:
          break
    video = video_format['format_id']

    if len(md.formats['audio']) == 0:
      # url doesn't support audio, download video only
      return video
    else:
      # Add as a bundled format for merging after download
      audio = md.formats['audio'][0]['format_id']
      return BundledFormat(video = video, audio = audio)
  
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
  """ select quality of the media to be downloaded """
  def _ask_format_option(self, md_ls:list[VideoMetaData], media : str) -> str:
    """
      Ask user to select format option if there are multiple options available
    """
    # if media is audio, select best quality
    if media == LazyMediaType.AUDIO.value:
      return LazyFormatType.BEST_QUALITY.value
    
    options = self._get_options(md_ls)
    if len(options) == 1:
      print('Only one format option available, select it automatically')
      print(f'Selected option: {Fore.CYAN}{options[0]}{Style.RESET_ALL}')
      return options[0]
    
    autofill_selection = get_lyd_format_autofill()
    if autofill_selection is not None:
      print('Format autofill found')
      print(f'Selected option: {Fore.CYAN}{options[autofill_selection]}{Style.RESET_ALL}')
      return options[autofill_selection]
    
    return inq_prompt([
      inq_List(
        'format_option', message=f'{Fore.CYAN}Select the video format{Style.RESET_ALL}', 
        choices=options, default=options[0]
      )
    ])['format_option']
                      
  def _get_options(self, md_ls:list[VideoMetaData]) -> list[str]:
    option_best_avaialble = True
    option_both_available = True
    for md in md_ls:
      if not option_both_available and not option_best_avaialble:
        break
      if len(md.formats['video']) == 0:
        option_best_avaialble = False
      if len(md.formats['both']) == 0:
        option_both_available = False

    options = []
    if option_best_avaialble:
      options.append(LazyFormatType.BEST_QUALITY.value)
      options.append(LazyFormatType.BEST_QUALITY_LOW_SIZE.value)
    if option_both_available:
      options.append(LazyFormatType.QUALITY_EFFICIENT.value)
    return options
# ============== lazy format selection ============== #
