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
  def __init__(self) -> None:
    self.opts = Opts()

  # main process
  def run (self, loop=True):
    print("----------------- Download -----------------", end='\n\n')

    while True:
      self.opts.reset()

      # ask url
      url = UrlSection(title='Url').run()
                      
      # ask Login
      LoginSection(title='Login').run(self.opts)
  
      # list subtitle
      ListSubtitleSection(title='List Subtitle').run(url, self.opts)

      # list format
      ListFormatSection(title='List Format').run(url, self.opts)
      
      # set up download
      # subtitle, format, output dir
      Section(title='Set up download').run(self.setup)
                                  
      # do download
      DownloadSection(title="Downloading").run(url=url, opts=self.opts)

      if not loop:
        break
  
  def setup(self):
    # subtitle
    SubTitleSection(
      title='Subtitle',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(self.opts)

    # format
    FormatSection(
      title='Format',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(self.opts)

    # output dir
    OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(self.opts, askName=False)

if __name__ == "__main__":
  Dl().run()