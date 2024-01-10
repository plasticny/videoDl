from yt_dlp import YoutubeDL

from src.section.Section import Section

from src.structs.option import IOpt, TOpt


class TListFormatOpt (TOpt):
  skip_download : bool
  listformats: bool


class ListFormatSection (Section):    
  def run(self, opts:IOpt) -> None:
    return super().run(self._listFormat, opts=opts.copy())

  def _listFormat (self, opts:IOpt):
    doList = input('List available format?(N) ').upper()
    if doList == 'N' or doList == '':
      return

    YoutubeDL(self._to_ytdlp_opt(opts)).download([opts.url])
    
  def _to_ytdlp_opt (self, opts:IOpt) -> TListFormatOpt:
    res : TListFormatOpt = {
      **IOpt.to_ytdlp_opt(opts),
      'skip_download': True,
      'listformats': True
    }
    return res