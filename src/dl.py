import service.packageChecker as packageChecker
packageChecker.check()

from section.Section import Section, HeaderType
from section.UrlSection import UrlSection
from section.LoginSection import LoginSection
from section.ListFormatSection import ListFormatSection
from section.DownloadSection import DownloadSection
from section.SubTitleSection import SubTitleSection
from section.FormatSection import FormatSection
from section.OutputSection import OutputSection

from service.YtDlpHelper import Opts
from service.MetaData import fetchMetaData, VideoMetaData
from service.fileHelper import perpare_temp_folder, clear_temp_folder

class Dl:
  def __init__ (self):
    self.title = 'Download'
  
  # main process
  def run (self, loop=True):
    print(f"----------------- {self.title} -----------------", end='\n\n')
    
    perpare_temp_folder()

    while True:
      # ask url
      url = UrlSection(title='Url').run()
                            
      # ask Login
      temp_opts : Opts = self.login(url, Opts())

      # fetch metadata
      print('Getting download informaton...', end='\n\n')
      md = fetchMetaData(url, temp_opts)
      
      # get video metadata list
      videos_md : list[VideoMetaData] = md.videos if md.isPlaylist() else [md]
      # prepare opts list
      opts_ls : list[Opts] = [temp_opts.copy() for _ in range(len(videos_md))]

      # set up download
      # subtitle, format, output dir
      opts_ls:list[Opts] = Section(title='Set up download').run(self.setup, md=md, opts_ls=opts_ls)
                                        
      # download
      assert len(videos_md) == len(opts_ls)
      for idx, (md, opts) in enumerate(zip(videos_md, opts_ls)):
        try:
          Section(title=f'Download video {idx+1} of {len(videos_md)}').run(
            self.download, opts=opts, md=md
          )
        finally:
          clear_temp_folder()

      if not loop:
        break
      
  def login(self, url, opts):
    return LoginSection(title='Login').run(opts)
  
  def setup(self, md:VideoMetaData, opts_ls:list[Opts]) -> list[Opts]:
    # list format
    ListFormatSection(title='List Format', headerType=HeaderType.SUB_HEADER).run(md.url, opts_ls[0])

    # format
    temp_opts = FormatSection(
      title='Format',
      headerType=HeaderType.SUB_HEADER
    ).run(opts_ls[0])
    
    for opts in opts_ls:
      opts.format = temp_opts.format
    
    # subtitle
    opts_ls = SubTitleSection(
      title='Subtitle',
      headerType=HeaderType.SUB_HEADER
    ).run(md, opts_ls=opts_ls)

    # output dir
    opts_ls = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts_ls=opts_ls, askName=False)

    return opts_ls

  def download(self, opts:Opts, md:VideoMetaData):
    DownloadSection(doShowHeader=False).run(md.url, opts)

if __name__ == "__main__":
  Dl().run()