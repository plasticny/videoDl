import service.packageChecker as packageChecker
packageChecker.check()

from colorama import Fore, Style

from section.Section import Section, HeaderType
from section.UrlSection import UrlSection
from section.LoginSection import LoginSection
from section.ListFormatSection import ListFormatSection
from section.DownloadSection import DownloadSection
from section.SubTitleSection import SubTitleSection
from section.FormatSection import FormatSection
from section.OutputSection import OutputSection

from service.YtDlpHelper import Opts
from service.MetaData import fetchMetaData, MetaData

class Dl:
  # main process
  def run (self, loop=True):
    print("----------------- Download -----------------", end='\n\n')

    while True:
      opts = Opts()

      # ask url
      url = UrlSection(title='Url').run()
                      
      # ask Login
      opts = LoginSection(title='Login').run(opts)

      print('Getting download informaton...', end='\n\n')
      md = fetchMetaData(url, opts)

      if md.isPlaylist():
        print(f'{Fore.YELLOW}Playlist is not supported in dl currently.{Style.RESET_ALL}')
        continue

      # list format
      ListFormatSection(title='List Format').run(url, opts)
      
      # set up download
      # subtitle, format, output dir
      opts = Section(title='Set up download').run(self.setup, md=md, opts=opts)
                                  
      # do download
      DownloadSection(title="Downloading").run(url=url, opts=opts)

      if not loop:
        break
  
  def setup(self, md:MetaData, opts:Opts) -> Opts:
    # subtitle
    opts_ls = SubTitleSection(
      title='Subtitle',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(md, opts_ls=[opts])

    # format
    opts = FormatSection(
      title='Format',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts_ls[0])

    # output dir
    opts_ls = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts_ls=[opts], askName=False)

    return opts_ls[0]

if __name__ == "__main__":
  Dl().run()