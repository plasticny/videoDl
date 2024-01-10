import src.service.packageChecker as packageChecker
packageChecker.check()

from src.service.urlHelper import getSource, UrlSource
from src.service.MetaData import VideoMetaData

from src.section.Section import HeaderType
from src.section.DownloadSection import DownloadOpt
from src.section.SubTitleSection import SubTitleSection
from src.section.OutputSection import OutputSection
from src.section.FormatSection import LazyFormatSection

from src.dl import Dl


class lazyYtDownload(Dl):
  def __init__(self):
    self.title = 'LYD'

  def login(self, url:str) -> str:
    """
      Overwirte Dl.login\n
      Only ask login if the url is from bilibili
    """
    if getSource(url) == UrlSource.BILIBILI:
      return super().login(url)
    return None

  def setup(self, md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    """
      Overwirte Dl.setup
      Select format with lazy format section
    """
    opt_ls = [DownloadOpt(md.opts) for md in md_ls]
    
    # select format
    selected_format = LazyFormatSection(
      title='Format',
      headerType=HeaderType.SUB_HEADER
    ).run(md_ls)
    
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
  lazyYtDownload().run()