"""
  Custom fetchers for getting info that is not provided or not easy to get from yt-dlp
"""
from urllib.request import build_opener, HTTPCookieProcessor
from json import loads as json_loads
from yt_dlp.cookies import load_cookies
from http.client import HTTPResponse
from colorama import Fore, Style

from src.structs.video_info import Subtitle, BiliBiliSubtitle


def get_bili_page_cids(bvid:str, cookie_file_path : str = None) -> list[str]:
  """
    Get all cids of page in a bilibili page list

    Args:
      bvid: suppose to be the id of the bilibili playlist instance
      opts: Opts instance for getting cookiefile path

    Returns:
      list[int]: cids
  """
  cookiejar = load_cookies(cookie_file_path, None, None)
  opener = build_opener(HTTPCookieProcessor(cookiejar))
  res : HTTPResponse = opener.open(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}')
  json = json_loads(res.read().decode('utf-8'))

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
  res : HTTPResponse = build_opener().open(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
  json = json_loads(res.read().decode('utf-8'))

  if json['code'] != 0:
    print(f'{Fore.RED}[bvid to aid] Bilibili fetcher error: return code != 0, bvid={bvid}{Style.RESET_ALL}')
    return ''
  
  return json['data']['aid']

def get_bili_subs(bvid:str, cid:int=None, cookie_file_path : str = None) -> tuple[list[Subtitle], list[Subtitle]]:
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

  cookiejar = load_cookies(cookie_file_path, None, None)
  opener = build_opener(HTTPCookieProcessor(cookiejar))
  res : HTTPResponse = opener.open(req_url)
  json = json_loads(res.read().decode('utf-8'))

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
