"""
  Custom fetcher for getting info that is not provided or not easy to get from yt-dlp
"""
from urllib.request import build_opener, HTTPCookieProcessor
from json import loads as json_loads
from yt_dlp.cookies import load_cookies
from http.client import HTTPResponse

from service.structs import Subtitle
from service.YtDlpHelper import Opts

class BiliBiliFetcher:
  @staticmethod
  def getSubtitles(bvid:str, opts:Opts=Opts()) -> (list[Subtitle], list[Subtitle]):
    """
      Get subtitles from bilibili

      Args:
        bvid: should be the id property of the VideoMetaData instance
        opts: Opts instance for getting cookiefile path

      Returns:
        (list[Subtitle], list[Subtitle]): (subtitles, autoSubtitles)
    """
    cookiejar = load_cookies(opts.cookieFile, None, None)
    opener = build_opener(HTTPCookieProcessor(cookiejar))
    res : HTTPResponse = opener.open(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
    json = json_loads(res.read().decode('utf-8'))

    # check if success
    # 暫時未找到方法獲取pages的字幕
    if json['code'] != 0:
      return ([], [])

    sub : list[Subtitle] = []
    auto_sub : list[Subtitle] = []

    for s in json['data']['subtitle']['list']:
      if s['ai_type'] == 0:
        sub.append(Subtitle(code=s['lan'], name=s['lan_doc'], isAuto=False))
      else:
        auto_sub.append(Subtitle(code=s['lan'], name=s['lan_doc'], isAuto=True))

    return (sub, auto_sub)