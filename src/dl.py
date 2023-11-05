import service.packageChecker as packageChecker
packageChecker.check()

from section.Section import Section, HeaderType
from section.UrlSection import UrlSection
from section.LoginSection import LoginSection
from section.ListSubtitleSection import ListSubtitleSection
from section.ListFormatSection import ListFormatSection
from section.DownloadSection import DownloadSection
from section.SubTitleSection import SubTitleSection
from section.FormatSection import FormatSection
from section.OutputSection import OutputSection

from service.YtDlpHelper import Opts

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
  
      # list subtitle
      ListSubtitleSection(title='List Subtitle').run(url, opts)
  
      # list format
      ListFormatSection(title='List Format').run(url, opts)
      
      # set up download
      # subtitle, format, output dir
      opts = Section(title='Set up download').run(self.setup, opts)
                                  
      # do download
      DownloadSection(title="Downloading").run(url=url, opts=opts)

      if not loop:
        break
  
  def setup(self, opts) -> Opts:
    # subtitle
    opts = SubTitleSection(
      title='Subtitle',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts)

    # format
    opts = FormatSection(
      title='Format',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts)

    # output dir
    opts = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts, askName=False)

    return opts

if __name__ == "__main__":
  Dl().run()