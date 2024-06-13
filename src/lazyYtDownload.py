from sys import path
from pathlib import Path
path.append(Path('.').resolve().as_posix())

from src.service.urlHelper import getSource, UrlSource
from src.service.MetaData import VideoMetaData

from src.section.Section import HeaderType
from src.section.DownloadSection import DownloadOpt
from src.section.SubTitleSection import SubTitleSection
from src.section.OutputSection import OutputSection 
from src.section.FormatSection import LazyFormatSection

from src.dl import Dl


class lazyYtDownload(Dl):
  def __init__(self, do_check_update : bool = False):
    super().__init__(do_check_update)
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
    lazy_format_ret = LazyFormatSection(
      title='Format',
      headerType=HeaderType.SUB_HEADER
    ).run(md_ls)
    
    # subtitle
    # not ask subtitle if the media is audio
    if lazy_format_ret.media == 'Video':
      selected_sub_ret = SubTitleSection(
        title='Subtitle',
        headerType=HeaderType.SUB_HEADER
      ).run(md_ls)
    else :
      selected_sub_ret = SubTitleSection.not_write_ret(md_ls)

    # output dir
    output_dir = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(askName=False)['dir']

    # assign options
    for idx, opt in enumerate(opt_ls):
      opt.set_media(lazy_format_ret.media)
      opt.set_format(lazy_format_ret.format_ls[idx])
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
  lazyYtDownload(do_check_update=True).run()