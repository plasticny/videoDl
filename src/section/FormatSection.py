from inquirer import prompt as inq_prompt, List as inq_List
from colorama import Fore, Style
from typing import Union, Literal

from src.section.Section import Section
from src.section.DownloadSection import BundledFormat

from src.service.MetaData import VideoMetaData
from src.service.autofill import get_lyd_format_autofill
  

class FormatSection (Section):
  def run(self) -> str:
    return super().run(self.__main)
  
  def __main(self) -> str:
    fo = input('Enter the format:(auto) ').lower()
    return 'mp4' if fo == '' or fo == 'auto' else fo


# ============== lazy format selection ============== #
class LazyFormatSection (Section):
  """
    Select format with some default options
    instead entering format
  """
  OPT_BEST_QUA = 'Best quality' # download best quality
  OPT_BEST_QUA_LOW_SIZE = 'Best quality lowest size' # download the lowest size of the best quality
  OPT_QUA_EFF = 'Quality-efficient balance' # download best quality, but avoid video editing
  
  def run(self, md_ls:list[VideoMetaData]) -> list[Union[str, BundledFormat]]:
    return super().run(self.__main, md_ls=md_ls)

  def __main(self, md_ls:list[VideoMetaData]) -> list[Union[str, BundledFormat]]:
    format_option = self._ask_format_option(md_ls)
    self.logger.info(f'Format option selected: {format_option}')
    
    res : list[Union[str, BundledFormat]] = []
    for md in md_ls:
      if format_option == self.OPT_QUA_EFF:
        selected_format = self._quality_efficient(md)
      elif format_option == self.OPT_BEST_QUA or format_option == self.OPT_BEST_QUA_LOW_SIZE:
        selected_format = self._best_quality(md, format_option)

      if isinstance(selected_format, BundledFormat):
        self.logger.info(f'[{md.title}] selected format: {selected_format.video} + {selected_format.audio}')
      else:
        self.logger.info(f'[{md.title}] selected format: {selected_format}')
      res.append(selected_format)

    return res
  
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
    if format_option == self.OPT_BEST_QUA_LOW_SIZE:
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

  # === Inquiry functions === #
  def _ask_format_option(self, md_ls:list[VideoMetaData]) -> str:
    """
      Ask user to select format option if there are multiple options available
    """    
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
      options.append(self.OPT_BEST_QUA)
      options.append(self.OPT_BEST_QUA_LOW_SIZE)
    if option_both_available:
      options.append(self.OPT_QUA_EFF)
    return options
  # === Inquiry functions === #
# ============== lazy format selection ============== #
