"""
  MetaData of the video or playlist to be downloaded.
  Use MetaData.fetchMetaData to get the metadata of the video or playlist.
"""
from __future__ import annotations
from typing import TypedDict
from abc import ABCMeta, abstractmethod

from sys import path as sysPath
sysPath.append('src')

from functools import cmp_to_key
from colorama import Fore, Style
from typing import Union

from src.service.urlHelper import getSource, UrlSource
from src.service.bilibili import get_bili_subs, get_bili_page_cids, bvid_2_aid
from src.service.logger import Logger
from src.service.ytdlp import Ytdlp

from src.structs.option import IOpt, TOpt
from src.structs.video_info import TFormatVideo, TFormatAudio, TFormatBoth, Subtitle

LOGGER = Logger()

def ytdlp_extract_metadata (opts:MetaDataOpt):
  return Ytdlp(MetaDataOpt.to_ytdlp_opt(opts)).extract_info(opts.url)

""" ========================= funcitons for get the metadata ========================= """
def fetchMetaData(opts:MetaDataOpt) -> Union[MetaData, None]:
  """
    Fetch metadata of the video or playlist to be downloaded\n
    Better use this function to get metadata instead of instantiating the metadata directly
  """
  assert isinstance(opts, MetaDataOpt)
  
  try:
    metadata = ytdlp_extract_metadata(opts)
  except Exception as e:
    LOGGER.error(f'Error when getting metadata: {e}')
    return None
  
  # instantiate the metadata
  source = getSource(opts.url)
  LOGGER.debug(f'Getting metadata from {source}')
  
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
  """ Playlist metadata """
  @property
  def playlist_count(self) -> int:
    return self.metadata['playlist_count']
  @property
  def video_urls(self) -> list[str]:
    return [v.url for v in self.videos]

  def __init__(self, metadata : dict, opts : MetaDataOpt) -> None:
    super().__init__(metadata, opts)
    self.videos = self.fetchVideoMd()

  def fetchVideoMd(self) -> list[VideoMetaData]:
    """ fetch metadata of videos in the playlist"""
    res = []
    for idx, entry in enumerate(self.metadata['entries']):
      print(f'{Fore.CYAN}Getting info of video {idx + 1} / {self.playlist_count}{Style.RESET_ALL}')
      
      entry_opts : MetaDataOpt = self.opts.copy()
      entry_opts.url = entry['url']
      
      videoMd = fetchMetaData(entry_opts)
      
      if videoMd is None:
        print(f'{Fore.RED}Skipped {entry_opts.url}, error when getting info of video.{Style.RESET_ALL}')
      else:
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
      # If a and b is video in the format, compare by resolution first
      IS_VIDEO = lambda x: 'vcodec' in x and x['vcodec'] != 'none'
      if IS_VIDEO(a) and IS_VIDEO(b) and a['resolution'] != b['resolution']:
        a_res = a['resolution'].split('x')
        b_res = b['resolution'].split('x')
        if a_res[0] != b_res[0]:
          return int(b_res[0]) - int(a_res[0])
        if a_res[1] != b_res[1]:
          return int(b_res[1]) - int(a_res[1])

      # Compare two formats by tsr, from high to low
      # If the format has no tsr, it will be placed at the end
      if 'tbr' not in a or a['tbr'] is None:
        return 1
      if 'tbr' not in b or b['tbr'] is None:
        return -1
      return b['tbr'] - a['tbr']
    
    sorted_raw_formats: list[dict] = sorted(self.metadata['formats'], key=cmp_to_key(__compare))
    # remove format that has no tsr
    # while len(sorted_raw_formats) > 0 and 'tbr' not in sorted_raw_formats[-1]:
    #   sorted_raw_formats.pop()
    
    # extract formats
    formats : TMdFormats = { 'audio': [], 'video': [], 'both': [] }
    for format in sorted_raw_formats:
      has_audio = format.get('acodec', 'none') != 'none' or format.get('format_note', '') == 'Audio'
      has_video = format.get('vcodec', 'none') != 'none'
      
      # for video, only accept mp4
      if has_video and format['ext'] != 'mp4':
        LOGGER.debug(f'format {format["format_id"]} skipped, not mp4')
        continue
      
      if 'tbr' not in format:
        LOGGER.debug(f'format {format["format_id"]} skipped, no tbr')
        continue

      basic_info = {
        'format_id': format['format_id'],
        'tbr': format['tbr']
      }
      audio : TFormatAudio = {
        **basic_info,
        'codec': format.get('acodec', 'none'),
        'ext': format['audio_ext']
      } if has_audio else None
      video : TFormatVideo = {
        **basic_info,
        'codec': format["vcodec"],
        'ext': format['video_ext'],
        'width': int(format['resolution'].split('x')[0]),
        'height': int(format['resolution'].split('x')[1])
      } if has_video else None
      
      if has_audio and has_video:
        LOGGER.debug(f'format {format["format_id"]} added to both')
        formats['both'].append({**basic_info, 'audio': audio, 'video': video})
      if has_audio and not has_video:
        # only accept format that has audio only
        LOGGER.debug(f'format {format["format_id"]} added to audio')
        formats['audio'].append(audio)  
      if has_video:
        LOGGER.debug(f'format {format["format_id"]} added to video')
        formats['video'].append(video)
      if not has_audio and not has_video:
        LOGGER.debug(f'format {format["format_id"]} skipped, no audio and video')

    # log extracted formats
    LOGGER.debug(f'Extracted audio formats: {formats["audio"]}')
    LOGGER.debug(f'Extracted video formats: {formats["video"]}')
    LOGGER.debug(f'Extracted both formats: {formats["both"]}')

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
