from sys import path
from pathlib import Path
path.append(Path('.').resolve().as_posix())

from colorama import Fore, Style

from src.section.Section import Section, HeaderType
from src.section.UrlSection import UrlSection
from src.section.LoginSection import LoginSection, LoginSectionRet
from src.section.DownloadSection import DownloadSection, DownloadOpt
from src.section.SubTitleSection import SubTitleSection
from src.section.FormatSection import FormatSection
from src.section.OutputSection import OutputSection

from src.service.MetaData import fetchMetaData, VideoMetaData, MetaDataOpt, PlaylistMetaData
from src.service.fileHelper import perpare_temp_folder, clear_temp_folder
from src.service.logger import Logger
from src.service.ytdlp import Ytdlp


class Dl:
  def __init__ (self, check_upgrade: bool = False):
    self.logger = Logger()
    self.title = 'Download'
    Ytdlp.ensure_installed()
    if check_upgrade:
      self.upgrade()
      
  def upgrade(self):
    print(f'{Fore.CYAN}Checking for updates...{Style.RESET_ALL}')
    Ytdlp.upgrade()
    print()
  
  # main process
  def run (self, loop: bool = True):
    self.logger.debug('======= Start download process =======')
    self.logger.clear()

    print(f"----------------- {self.title} -----------------", end='\n\n')

    perpare_temp_folder()
    
    is_first_started = False

    while not is_first_started or loop:
      is_first_started = True
      
      URL = UrlSection(title='Url').run()
      login_ret = self.login(URL)

      # option for get metadata
      # the info stored in this opt object suppose will be used in the future
      md_opt: MetaDataOpt = MetaDataOpt()
      md_opt.url = URL
      if login_ret.do_login:
        if login_ret.cookie_file_path is not None:
          md_opt.cookie_file_path = login_ret.cookie_file_path
        else:
          md_opt.login_browser = login_ret.browser

      try:
        md_ls = self.get_metadata(md_opt)
      except Exception as e:
        print(f'\n{Fore.RED}Download Failed, error on getting url info{Style.RESET_ALL}\n')
        self.logger.error(str(e.with_traceback(None)))
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

  def login(self, url: str) -> LoginSectionRet:
    """ return cookie file path """
    return LoginSection(title='Login').run(url)
  
  def get_metadata(self, opt: MetaDataOpt) -> list[VideoMetaData]:
    """
      get metadata of the url\n
      raise exception if fetch metadata failed
    """
    print('Getting download informaton...', end='\n\n')      

    try:
      md = fetchMetaData(opt)
      if isinstance(md, PlaylistMetaData):
        return md.videos
      return [md]
    except:
      raise Exception('Failed to get video metadata')
  
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
