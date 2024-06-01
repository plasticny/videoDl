"""
  MetaData of the video or playlist to be downloaded.
  Use MetaData.fetchMetaData to get the metadata of the video or playlist.
"""
from __future__ import annotations
from typing import TypedDict
from abc import ABCMeta, abstractmethod

from sys import path as sysPath
sysPath.append('src')

from yt_dlp import YoutubeDL
from contextlib import redirect_stdout
from io import StringIO
from functools import cmp_to_key
from colorama import Fore, Style

from src.service.urlHelper import getSource, UrlSource
from src.service.bilibili import get_bili_subs, get_bili_page_cids, bvid_2_aid
from src.service.logger import Logger

from src.structs.option import IOpt, TOpt
from src.structs.video_info import TFormatVideo, TFormatAudio, TFormatBoth, TFormatDesc, Subtitle


def ytdlp_extract_metadata (opts:MetaDataOpt):
  try:
    # quiet=True also print subtitle, redirect stdout to hide it
    with redirect_stdout(StringIO()), YoutubeDL(MetaDataOpt.to_ytdlp_opt(opts)) as ydl:
      # download basic metadata using yt-dlp
      metadata = ydl.extract_info(opts.url, download = False)
      metadata : dict = ydl.sanitize_info(metadata)

      logger = Logger()
      json_name = logger.dump_dict(metadata)
      logger.debug(f'Metadata of {opts.url} has been saved to {json_name}.json')

  except Exception as e:
    print(e)
    raise Exception('Get metadata failed')
  
  return metadata


""" ========================= funcitons for get the metadata ========================= """
def fetchMetaData(opts:MetaDataOpt) -> MetaData:
  """
    Fetch metadata of the video or playlist to be downloaded\n
    Better use this function to get metadata instead of instantiating the metadata directly
  """
  assert isinstance(opts, MetaDataOpt)  
  metadata = ytdlp_extract_metadata(opts)
  
  # instantiate the metadata
  source = getSource(opts.url)
  Logger().debug(f'Getting metadata from {source}')
  
  if metadata['_type'] == 'playlist':
    if source is UrlSource.BILIBILI:
      return BiliBiliPlaylistMetaData(metadata, opts)
    else:
      return PlaylistMetaData(metadata, opts)
  else:
    if source is UrlSource.BILIBILI:
      return BiliBiliVideoMetaData(metadata, opts)
    elif source is UrlSource.FACEBOOK:
      return FacebookVideoMetaData(metadata, opts)
    elif source is UrlSource.IG:
      return IGVideoMetaData(metadata, opts)
    else:
      return VideoMetaData(metadata, opts)
    
def fetch_bili_page_metadata (opts:MetaData, cid:str) -> BiliBiliVideoMetaData:
  assert isinstance(opts, MetaDataOpt)
  assert getSource(opts.url) is UrlSource.BILIBILI
  return BiliBiliVideoMetaData(ytdlp_extract_metadata(opts), opts, cid)
""" ========================= funcitons for get the metadata ========================= """


# ========================= typing ========================= #
class TMetaDataOpt (TOpt):
  quiet : bool
  extract_flat : bool
  listsubtitles : bool

class TMdFormats (TypedDict):
  video: list[TFormatVideo] # formats that support video
  audio: list[TFormatAudio] # formats that support audio
  both: list[TFormatBoth] # formats that support both audio and video
# ========================= typing ========================= #


# ========================= options ========================= #
class MetaDataOpt (IOpt):
  """ Necessary options for fetching MetaData """
  @staticmethod
  def to_ytdlp_opt(obj : MetaDataOpt) -> TMetaDataOpt:
    return {
      **IOpt.to_ytdlp_opt(obj),
      'quiet': True,
      'extract_flat': True,
      # use bilibili api to get bilibili subtitles
      'listsubtitles': getSource(obj.url) is not UrlSource.BILIBILI,
    } 
    
  def __init__(self) -> None:
    super().__init__()
# ========================= options ========================= #


# ========================== Abstract MetaData ========================= #  
class MetaData (metaclass = ABCMeta):
  @property
  def title(self) -> str:
    return self.metadata['title']
  @property
  def url(self) -> str:
    return self.metadata['original_url']
  @property
  def id(self) -> str:
    return self.metadata['id']
  
  @abstractmethod
  def __init__ (self, metadata : dict, opts : MetaDataOpt):
    self.metadata = metadata
    self.opts = opts.copy()

  def isPlaylist(self) -> bool:
    return isinstance(self, PlaylistMetaData)
# ========================== End Abstract MetaData ========================= #


# ========================== Playlist ========================= #
class PlaylistMetaData (MetaData):
  """Playlist metadata"""
  @property
  def playlist_count(self) -> int:
    return self.metadata['playlist_count']
  @property
  def video_urls(self) -> list[str]:
    return [v.url for v in self.videos]

  def __init__(self, metadata, opts : MetaDataOpt) -> None:
    super().__init__(metadata, opts)
    self.videos = self.fetchVideoMd()
    
  def fetchVideoMd(self) -> list[VideoMetaData]:
    res = []
    for idx, entry in enumerate(self.metadata['entries']):
      print(f'{Fore.CYAN}Getting info of video {idx + 1} / {self.playlist_count}{Style.RESET_ALL}')
      
      entry_opts : MetaDataOpt = self.opts.copy()
      entry_opts.url = entry['url']
      
      videoMd = fetchMetaData(entry_opts)
      assert not videoMd.isPlaylist()
      res.append(videoMd)
    return res
  
class BiliBiliPlaylistMetaData (PlaylistMetaData):
  """Playlist metadata of bilibili"""
  def __init__(self, metadata, opts:MetaDataOpt):
    super().__init__(metadata, opts)
    # specify the type of prop videos
    self.videos : list[BiliBiliVideoMetaData] = self.videos

  def fetchVideoMd(self) -> list[BiliBiliVideoMetaData]:
    cids = get_bili_page_cids(self.id, self.opts.cookie_file_path)

    res = []
    for entry, cid in zip(self.metadata['entries'], cids):
      entry_opts:MetaDataOpt = self.opts.copy()
      entry_opts.url = entry['url']

      videoMd = fetch_bili_page_metadata(entry_opts, cid)
      res.append(videoMd)
    return res
# ========================== End Playlist ========================= #


# ========================== Video ========================= #
class VideoMetaData (MetaData):
  """Video metadata"""
  @property
  def formats(self) -> TMdFormats:
    return self._format
  
  def __init__(self, metadata, opts : MetaDataOpt):
    super().__init__(metadata, opts)

    # subtitle
    sub, auto_sub = self._getSubtitles()
    self.subtitles = sub
    self.autoSubtitles = auto_sub

    # format
    self._format = self._extract_format()
    
  def _getSubtitles(self) -> tuple[list[Subtitle], list[Subtitle]]:
    def __restruct_sub_info(sub_info:dict, isAuto:bool=False):
      res = []
      for code, subs in sub_info.items():
        # find name
        for sub in subs:
          if 'name' in sub:
            res.append(Subtitle(code, sub['name'], isAuto))
            break
        else:
          # if name not found, use code as name
          res.append(Subtitle(code, code, isAuto))
      return res
    
    if 'subtitles' not in self.metadata.keys():
      return [], []
    
    sub = __restruct_sub_info(self.metadata['subtitles'])
    if 'automatic_captions' in self.metadata.keys():
      auto_sub = __restruct_sub_info(self.metadata['automatic_captions'], True)
    else:
      auto_sub = []
      
    return sub, auto_sub
      
  def _extract_format (self) -> TMdFormats:    
    def __compare(a, b):
      # Compare two formats by tsr, from high to low
      # If the format has no tsr, it will be placed at the end
      if 'tbr' not in a or a['tbr'] is None:
        return 1
      if 'tbr' not in b or b['tbr'] is None:
        return -1
      return b['tbr'] - a['tbr']
    
    sorted_raw_formats = sorted(self.metadata['formats'], key=cmp_to_key(__compare))
    # remove format that has no tsr
    while len(sorted_raw_formats) > 0 and 'tbr' not in sorted_raw_formats[-1]:
      sorted_raw_formats.pop()
    
    formats : TMdFormats = { 'audio': [], 'video': [], 'both': [] }
    for format in sorted_raw_formats:
      has_audio = 'acodec' in format and format['acodec'] != 'none'
      has_video = 'vcodec' in format and format['vcodec'] != 'none'
      
      # for video, only accept mp4
      if has_video and format['ext'] != 'mp4':
        continue
      
      basic_info = {
        'format_id': format['format_id'],
        'tbr': format['tbr']
      }
      audio : TFormatDesc = {
        'codec': format["acodec"],
        'ext': format['audio_ext']
      } if has_audio else None
      video : TFormatDesc = {
        'codec': format["vcodec"],
        'ext': format['video_ext']
      } if has_video else None
      
      if has_audio and has_video:
        formats['both'].append({
          **basic_info,
          'audio': audio,
          'video': video
        })
      if has_audio:
        formats['audio'].append({
          **basic_info,
          'audio': audio
        })
      if has_video:
        formats['video'].append({
          **basic_info,
          'video': video
        })

    return formats

class BiliBiliVideoMetaData (VideoMetaData):
  """
    Video metadata of bilibili
    
    Args:
      cid: cid of the video, should be given if the video is in a playlist
  """
  def __init__(self, metadata, opts: MetaDataOpt, cid:str = None):
    self.bvid : str = metadata['id'].split('_')[0]
    self.cid : str = cid
    self.aid : str = bvid_2_aid(self.bvid)
    super().__init__(metadata, opts)    

  def _getSubtitles(self) -> None:
    return get_bili_subs(self.bvid, self.cid, self.opts.cookie_file_path)

class FacebookVideoMetaData (VideoMetaData):
  def _extract_format(self) -> TMdFormats:
    formats = super()._extract_format()
    
    all_format_id = [f['format_id'] for f in self.metadata['formats']]
    for id in ['hd', 'sd']:
      if id not in all_format_id:
        continue
      # not append to video and audio because it is hard to esitmate the tbr
      formats['both'].append({
        'format_id': id,
        'audio': { 'codec': 'avc', 'ext': 'avc' },
        'video': { 'codec': 'aac', 'ext': 'aac' }
      })
    
    return formats
  
class IGVideoMetaData (VideoMetaData):
  def _extract_format(self) -> TMdFormats:
    def __compare(a, b):
      a_res = a['height'] * a['width']
      b_res = b['height'] * b['width']
      return b_res - a_res
    
    sorted_raw_formats = sorted(self.metadata['formats'], key=cmp_to_key(__compare))
    
    formats : TMdFormats = {
      'audio': [], 'video': [],
      'both': [{
        'format_id': f['format_id'],
        'audio': { 'codec': 'aac', 'ext': 'aac' },
        'video': { 'codec': 'mp4', 'ext': 'mp4' }
      } for f in sorted_raw_formats]
    }
    assert len(formats['both']) > 0  
    
    return formats
# ========================== End Video ========================= #
