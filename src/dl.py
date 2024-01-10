import src.service.packageChecker as packageChecker
packageChecker.check()

from src.section.Section import Section, HeaderType
from src.section.UrlSection import UrlSection
from src.section.LoginSection import LoginSection
from src.section.ListFormatSection import ListFormatSection
from src.section.DownloadSection import DownloadSection, DownloadOpt
from src.section.SubTitleSection import SubTitleSection
from src.section.FormatSection import FormatSection
from src.section.OutputSection import OutputSection

from src.service.MetaData import fetchMetaData, VideoMetaData, MetaDataOpt
from src.service.fileHelper import perpare_temp_folder, clear_temp_folder


class Dl:
  # main process
  def run (self, loop=True):    
    print(f"----------------- Download -----------------", end='\n\n')

    perpare_temp_folder()

    while True:
      URL = UrlSection(title='Url').run()
      COOKIE_FILE_PATH = self.login(URL)

      md_ls = self.get_metadata(URL, COOKIE_FILE_PATH)

      # subtitle, format, output dir
      opts_ls : list[DownloadOpt] = Section(title='Set up download').run(self.setup, md_ls=md_ls)

      # download
      assert len(md_ls) == len(opts_ls)
      for idx, opts in enumerate(opts_ls):
        try:
          Section(title=f'Download video {idx+1} of {len(opts_ls)}').run(
            DownloadSection(doShowHeader=False).run, opts=opts
          )
        finally:
          clear_temp_folder()

      if not loop:
        break

  def login(self, url:str):
    """ return cookie file path """
    return LoginSection(title='Login').run()
  
  def get_metadata(self, url:str, cookie_file_path:str) -> list[VideoMetaData]:
    opt : MetaDataOpt = MetaDataOpt()
    opt.url = url
    opt.cookie_file_path = cookie_file_path
    
    print('Getting download informaton...', end='\n\n')      
    md = fetchMetaData(opt)
    
    # get video metadata list
    return md.videos if md.isPlaylist() else [md]
  
  def setup(self, md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    opt_ls = [DownloadOpt(md.opts) for md in md_ls]
        
    # list format
    ListFormatSection(title='List Format', headerType=HeaderType.SUB_HEADER).run(opt_ls[0])

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
  Dl().run()