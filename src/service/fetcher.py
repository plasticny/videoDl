"""
  Custom fetchers for getting info that is not provided or not easy to get from yt-dlp
"""
from urllib.request import build_opener, HTTPCookieProcessor
from json import loads as json_loads
from yt_dlp.cookies import load_cookies
from http.client import HTTPResponse
from colorama import Fore, Style

from service.structs import Subtitle
from service.YtDlpHelper import Opts

class BiliBiliFetcher:
  @staticmethod
  def get_page_cids(bvid:str, opts:Opts=Opts()) -> list[int]:
    """
      Get all cids of page in a bilibili page list

      Args:
        bvid: suppose to be the id of the bilibili playlist instance
        opts: Opts instance for getting cookiefile path

      Returns:
        list[int]: cids
    """
    cookiejar = load_cookies(opts.cookieFile, None, None)
    opener = build_opener(HTTPCookieProcessor(cookiejar))
    res : HTTPResponse = opener.open(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}')
    json = json_loads(res.read().decode('utf-8'))

    if json['code'] != 0:
      # if error
      print(f'{Fore.RED}[Get page cids] Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
      return []
    
    return [page['cid'] for page in json['data']]

  @staticmethod
  def getSubtitles(id:str, opts:Opts=Opts(), cid:int=None) -> (list[Subtitle], list[Subtitle]):
    """
      Get subtitles from bilibili

      Args:
        id: the id property of the VideoMetaData instance
        opts: Opts instance for getting cookiefile path
        cid: the cid property of BiliBiliVideoMetaData instance, for getting subtitles of a page in pagelist

      Returns:
        (list[Subtitle], list[Subtitle]): (subtitles, autoSubtitles)
    """
    # parse yt-dlp id to bvid
    # yt-dlp bilibili id structure: {bvid} + (_p{page_no} if it is a page in playlist)
    bvid = id.split('_')[0]

    req_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    if cid is not None:
      req_url += f'&cid={cid}'

    cookiejar = load_cookies(opts.cookieFile, None, None)
    opener = build_opener(HTTPCookieProcessor(cookiejar))
    res : HTTPResponse = opener.open(req_url)
    json = json_loads(res.read().decode('utf-8'))

    if json['code'] != 0:
      # if error
      print(f'{Fore.RED}Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
      return ([], [])
    
    sub : list[Subtitle] = []
    auto_sub : list[Subtitle] = []
    for s in json['data']['subtitle']['list']:
      if s['ai_status'] == 0:
        sub.append(Subtitle(code=s['lan'], name=s['lan_doc'], isAuto=False))
      else:
        auto_sub.append(Subtitle(code=s['lan'], name=s['lan_doc'], isAuto=True))

    return (sub, auto_sub)