"""
  Custom fetchers for getting info that is not provided or not easy to get from yt-dlp
"""
from colorama import Fore, Style
from json import loads as json_loads
from os import access as os_access, R_OK as OS_R_OK
from typing import Optional, Any
from urllib.request import build_opener, HTTPCookieProcessor

from src.party3rd.YoutubeDLCookieJar import YoutubeDLCookieJar

from src.structs.video_info import Subtitle, BiliBiliSubtitle

def _get_cookie_jar (cookie_file_path : Optional[str] = None) -> YoutubeDLCookieJar:
  """ simulate yt-dlp's load_cookies """
  if cookie_file_path is None:
    return YoutubeDLCookieJar()
  
  is_filename = YoutubeDLCookieJar.is_path_like(cookie_file_path)
  if is_filename:
    cookie_file_path = YoutubeDLCookieJar.expand_path(cookie_file_path)

  cookiejar = YoutubeDLCookieJar(cookie_file_path)
  if not is_filename or os_access(cookie_file_path, OS_R_OK):
    cookiejar.load()
    
  return cookiejar

def _fetch (url : str, cookie_file_path : Optional[str] = None) -> dict[str, Any]:
  """ Return fetch result in json format """
  cookiejar = _get_cookie_jar(cookie_file_path)
  
  opener = build_opener(HTTPCookieProcessor(cookiejar))
  opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ')
  ]
    
  return json_loads(opener.open(url).read().decode('utf-8'))

def get_bili_page_cids(bvid:str, cookie_file_path: Optional[str] = None) -> list[str]:
  """
    Get all cids of page in a bilibili page list

    Args:
      bvid: suppose to be the id of the bilibili playlist instance
      opts: Opts instance for getting cookiefile path

    Returns:
      list[int]: cids
  """
  json = _fetch(
    f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}',
    cookie_file_path
  )

  if json['code'] != 0:
    print(f'{Fore.RED}[Get page cids] Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
    return []
  
  return [page['cid'] for page in json['data']]

def bvid_2_aid(bvid:str) -> str:
  """
    Get aid from bvid

    Args:
      bvid: suppose to be the id of the bilibili playlist instance
      opts: Opts instance for getting cookiefile path

    Returns:
      str: aid
  """
  json = _fetch(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')

  if json['code'] != 0:
    print(f'{Fore.RED}[bvid to aid] Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
    return ''
  
  return json['data']['aid']

def get_bili_subs(bvid:str, cid: Optional[int] = None, cookie_file_path: Optional[str] = None) -> tuple[list[Subtitle], list[Subtitle]]:
  """
    Get subtitles from bilibili

    Args:
      id: the id property of the VideoMetaData instance
      opts: Opts instance for getting cookiefile path
      cid: the cid property of BiliBiliVideoMetaData instance, for getting subtitles of a page in pagelist

    Returns:
      (list[Subtitle], list[Subtitle]): (subtitles, autoSubtitles)
  """
  req_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
  if cid is not None:
    req_url += f'&cid={cid}'

  json = _fetch(req_url, cookie_file_path)

  if json['code'] != 0:
    print(f'{Fore.RED}Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
    return ([], [])
  
  sub : list[Subtitle] = []
  auto_sub : list[Subtitle] = []
  for s in json['data']['subtitle']['list']:
    sub_obj = BiliBiliSubtitle(code=s['lan'], name=s['lan_doc'], ai_status=s['ai_status'])
    if s['ai_status'] == 0:
      sub.append(sub_obj)
    else:
      auto_sub.append(sub_obj)

  return (sub, auto_sub)
