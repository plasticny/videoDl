"""
  Custom fetcher for getting info that is not provided or not easy to get from yt-dlp
"""
from urllib.request import build_opener, HTTPCookieProcessor
from json import loads as json_loads
from yt_dlp.cookies import load_cookies
from http.client import HTTPResponse
from colorama import Fore, Style

from service.structs import Subtitle
from service.YtDlpHelper import Opts

class BiliBiliFetcher:
  # ========== static variable ========== #
  """
    an 1-size buffer for storing the latest subtitle info.
    for reducing the number of request when getting subtitle info from same playlist.
    update when fetching subtitle info from bilibili video that has different bvid.
    /// can read it, but DO NOT CHANGE IT IN OTHER PLACE ///

    structure: (bvid, subtitles, autoSubtitles)
  """
  __subtitle_buffer : (str, list[Subtitle], list[Subtitle]) = None
  # ========== static variable ========== #

  @staticmethod
  def getSubtitles(id:str, opts:Opts=Opts()) -> (list[Subtitle], list[Subtitle]):
    """
      Get subtitles from bilibili

      Args:
        id: the id property of the VideoMetaData instance
        opts: Opts instance for getting cookiefile path

      Returns:
        (list[Subtitle], list[Subtitle]): (subtitles, autoSubtitles)
    """
    # parse yt-dlp id to bvid
    # assume that all page in playlist have the same subtitles
    # yt-dlp bilibili id structure: {bvid} + (_p{page_no} if it is a page in playlist)
    bvid = id.split('_')[0]

    if BiliBiliFetcher.__subtitle_buffer is not None and BiliBiliFetcher.__subtitle_buffer[0] == bvid:
      # if buffer store the requested subtitles, return it
      return BiliBiliFetcher.__subtitle_buffer[1:]

    cookiejar = load_cookies(opts.cookieFile, None, None)
    opener = build_opener(HTTPCookieProcessor(cookiejar))
    res : HTTPResponse = opener.open(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
    json = json_loads(res.read().decode('utf-8'))

    if json['code'] != 0:
      # if error
      print(f'{Fore.RED}Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
      return ([], [])
    
    sub : list[Subtitle] = []
    auto_sub : list[Subtitle] = []
    for s in json['data']['subtitle']['list']:
      if s['ai_type'] == 0:
        sub.append(Subtitle(code=s['lan'], name=s['lan_doc'], isAuto=False))
      else:
        auto_sub.append(Subtitle(code=s['lan'], name=s['lan_doc'], isAuto=True))

    # update buffer
    BiliBiliFetcher.__subtitle_buffer = (bvid, sub, auto_sub)

    return (sub, auto_sub)