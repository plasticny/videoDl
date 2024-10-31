from sys import path
from pathlib import Path
path.append(Path('.').resolve().as_posix())

from colorama import Fore, Style

from src.section.Section import Section, HeaderType
from src.section.UrlSection import UrlSection
from src.section.LoginSection import LoginSection
from src.section.DownloadSection import DownloadSection, DownloadOpt
from src.section.SubTitleSection import SubTitleSection
from src.section.FormatSection import FormatSection
from src.section.OutputSection import OutputSection

from src.service.MetaData import fetchMetaData, VideoMetaData, MetaDataOpt
from src.service.fileHelper import perpare_temp_folder, clear_temp_folder
from src.service.logger import Logger
from src.service.ytdlp import Ytdlp


class Dl:
  def __init__ (self, check_upgrade = False):
    self.logger = Logger()
    self.title = 'Download'
    if check_upgrade:
      self.upgrade()
      
  def upgrade(self):
    print(f'{Fore.CYAN}Checking for updates...{Style.RESET_ALL}')
    Ytdlp.upgrade()
    print()
  
  # main process
  def run (self, loop=True):
    self.logger.debug('======= Start download process =======')
    self.logger.clear()

    print(f"----------------- {self.title} -----------------", end='\n\n')

    perpare_temp_folder()
    
    is_first_started = False

    while not is_first_started or loop:
      is_first_started = True
      
      URL = UrlSection(title='Url').run()
      COOKIE_FILE_PATH = self.login(URL)

      try:
        md_ls = self.get_metadata(URL, COOKIE_FILE_PATH)
      except Exception as e:
        print(f'\n{Fore.RED}Download Failed, error on getting url info{Style.RESET_ALL}\n')
        self.logger.error(str(e))
        continue

      # subtitle, format, output dir
      try:
        opts_ls : list[DownloadOpt] = Section(title='Set up download').run(self.setup, md_ls=md_ls)
      except Exception as e:
        print(f'\n{Fore.RED}{str(e)}{Style.RESET_ALL}\n')
        self.logger.error(str(e))
        continue

      # download all video in the url
      for idx, opts in enumerate(opts_ls):
        try:
          Section(title=f'Download video {idx+1} of {len(opts_ls)}').run(
            DownloadSection(doShowHeader=False).run, opts=opts
          )
        except Exception as e:
          print(f'\n{Fore.RED}Failed on downloading video{Style.RESET_ALL}\n')
          self.logger.error(str(e))
        finally:
          clear_temp_folder()

  def login(self, url:str):
    """ return cookie file path """
    return LoginSection(title='Login').run(url)
  
  def get_metadata(self, url:str, cookie_file_path:str) -> list[VideoMetaData]:
    """
      get metadata of the url\n
      raise exception if fetch metadata failed
    """
    opt : MetaDataOpt = MetaDataOpt()
    opt.url = url
    opt.cookie_file_path = cookie_file_path
    
    print('Getting download informaton...', end='\n\n')      
    md = fetchMetaData(opt)
    
    if md is None:
      raise Exception('Failed to get video metadata')
    
    # get video metadata list
    return md.videos if md.isPlaylist() else [md]
  
  def setup(self, md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    opt_ls = [DownloadOpt(md.opts) for md in md_ls]
        
    # format
    selected_format = FormatSection(
      title='Format',
      headerType=HeaderType.SUB_HEADER
    ).run()
    
    # subtitle
    selected_sub_ret = SubTitleSection(
      title='Subtitle',
      headerType=HeaderType.SUB_HEADER
    ).run(md_ls)

    # output dir
    output_dir = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(askName=False)['dir']
    
    # assign options
    for idx, opt in enumerate(opt_ls):
      opt.set_format(selected_format)
      opt.set_subtitle(
        selected_sub_ret['subtitle_ls'][idx],
        selected_sub_ret['do_embed'],
        selected_sub_ret['do_burn']
      )
      opt.output_dir = output_dir
      opt.output_nm = md_ls[idx].title

    return opt_ls

""" Entry """
if __name__ == "__main__":
  Dl(check_upgrade=True).run()
