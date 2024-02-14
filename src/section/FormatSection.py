from inquirer import prompt as inq_prompt, List as inq_List
from colorama import Fore, Style
from typing import Union

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
    Select format with some default options (best quality / quality-efficient balance)
    instead entering format
  """
  OPT_BEST_QUA = 'Best quality'
  OPT_QUA_EFF = 'Quality-efficient balance'
  
  def run(self, md_ls:list[VideoMetaData]) -> list[Union[str, BundledFormat]]:
    return super().run(self.__main, md_ls=md_ls)

  def __main(self, md_ls:list[VideoMetaData]) -> list[Union[str, BundledFormat]]:
    format_option = self._ask_format_option(md_ls)
    
    res : list[Union[str, BundledFormat]] = []
    for md in md_ls:
      if format_option == self.OPT_QUA_EFF and len(md.formats['both']) > 0:
        # if select quality-efficient balance and,
        # there is a format that support both video and audio
        res.append(md.formats['both'][0]['format_id'])
      elif len(md.formats['audio']) == 0:
        # url doesn't support audio, download video only
        res.append(md.formats['video'][0]['format_id'])
      else:
        # Download highest quality video and audio format and merge them
        # This is supposed to be the best quality
        res.append(BundledFormat(
          video=md.formats['video'][0]['format_id'],
          audio=md.formats['audio'][0]['format_id']
        ))
    return res

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
    if option_both_available:
      options.append(self.OPT_QUA_EFF)
    return options
  # === Inquiry functions === #
# ============== lazy format selection ============== #
