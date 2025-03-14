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
from typing import Any, Callable, Optional, Union

from src.service.urlHelper import getSource, UrlSource
from src.service.bilibili import get_bili_subs, get_bili_page_cids, bvid_2_aid
from src.service.logger import Logger
from src.service.ytdlp import Ytdlp

from src.structs.option import Opt, TOpt
from src.structs.video_info import TFormatVideo, TFormatAudio, TFormatBoth, Subtitle

LOGGER = Logger()

def ytdlp_extract_metadata (opts:MetaDataOpt):
  assert opts.url is not None
  return Ytdlp(MetaDataOpt.to_ytdlp_opt(opts)).extract_info(opts.url)

""" ========================= funcitons for get the metadata ========================= """
def fetchMetaData(opts:MetaDataOpt) -> Union[VideoMetaData, PlaylistMetaData]:
  """
    Fetch metadata of the video or playlist to be downloaded\n
    Better use this function to get metadata instead of instantiating the metadata directly
  """
  assert isinstance(opts, MetaDataOpt)
  
  try:
    metadata = ytdlp_extract_metadata(opts)
  except Exception as e:
    LOGGER.error(f'Error when getting metadata: {e.with_traceback(None)}')
    raise e
  
  # instantiate the metadata
  assert opts.url is not None
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
    else:
      return VideoMetaData(metadata, opts)
    
def fetch_bili_page_metadata (opts: MetaDataOpt, cid: int) -> BiliBiliVideoMetaData:
  assert isinstance(opts, MetaDataOpt)
  assert opts.url is not None
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
class MetaDataOpt (Opt):
  """ Necessary options for fetching MetaData """
  @staticmethod
  def to_ytdlp_opt(obj: Opt) -> TMetaDataOpt:
    assert isinstance(obj, MetaDataOpt), 'obj is not an instance of MetaDataOpt'
    assert obj.url is not None, 'url is not set'
    return {
      **Opt.to_ytdlp_opt(obj),
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
  def __init__ (self, metadata: dict[str, Any], opts : MetaDataOpt):
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

  def __init__(self, metadata: dict[str, Any], opts : MetaDataOpt) -> None:
    super().__init__(metadata, opts)
    self.videos = self.fetchVideoMd()

  def fetchVideoMd(self) -> list[VideoMetaData]:
    """ fetch metadata of videos in the playlist"""
    res: list[VideoMetaData] = []
    for idx, entry in enumerate(self.metadata['entries']):
      print(f'{Fore.CYAN}Getting info of video {idx + 1} / {self.playlist_count}{Style.RESET_ALL}')
      
      entry_opts : MetaDataOpt = self.opts.copy()
      entry_opts.url = entry['url']
      
      try:
        videoMd = fetchMetaData(entry_opts)
        assert not videoMd.isPlaylist() and isinstance(videoMd, VideoMetaData)
        res.append(videoMd)
      except:
        print(f'{Fore.RED}Skipped {entry_opts.url}, error when getting info of video.{Style.RESET_ALL}')
      
    return res
  
class BiliBiliPlaylistMetaData (PlaylistMetaData):
  """Playlist metadata of bilibili"""
  def __init__(self, metadata: dict[str, Any], opts:MetaDataOpt):
    super().__init__(metadata, opts)
    # specify the type of prop videos
    self.videos : list[BiliBiliVideoMetaData] = self.videos

  def fetchVideoMd (self) -> list[BiliBiliVideoMetaData]:
    cids = get_bili_page_cids(self.id, self.opts.cookie_file_path)

    res: list[BiliBiliVideoMetaData] = []
    for entry, cid in zip(self.metadata['entries'], cids):
      entry_opts = self.opts.copy()
      entry_opts.url = entry['url']

      videoMd = fetch_bili_page_metadata(entry_opts, int(cid))
      res.append(videoMd)
    return res
# ========================== End Playlist ========================= #


# ========================== Video ========================= #
class VideoMetaData (MetaData):
  """Video metadata"""
  @property
  def formats(self) -> TMdFormats:
    return self._format
  
  def __init__(self, metadata: dict[str, Any], opts : MetaDataOpt):
    super().__init__(metadata, opts)

    # subtitle
    sub, auto_sub = self._getSubtitles()
    self.subtitles = sub
    self.autoSubtitles = auto_sub
    LOGGER.info(f'Extracted subtitles: {self.subtitles}')
    LOGGER.info(f'Extracted automatic subtitles: {self.autoSubtitles}')

    # format
    self._format = self._extract_format()
    LOGGER.info(f'Extracted formats: {self._format}')
    
  def _getSubtitles(self) -> tuple[list[Subtitle], list[Subtitle]]:
    def __restruct_sub_info(sub_info: dict[str, Any], isAuto: bool = False) -> list[Subtitle]:
      res: list[Subtitle] = []
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
      
  def _compare_format (self, a: dict[str, Any], b: dict[str, Any]) -> int:
    # If a and b is video in the format, compare by resolution first
    IS_VIDEO: Callable[[dict[str, Any]], bool] = lambda x: 'vcodec' in x and x['vcodec'] != 'none'
    if IS_VIDEO(a) and IS_VIDEO(b) and a['resolution'] != b['resolution']:
      a_res: list[str] = a['resolution'].split('x')
      b_res: list[str] = b['resolution'].split('x')
      if a_res[0] != b_res[0]:
        return int(b_res[0]) - int(a_res[0])
      if a_res[1] != b_res[1]:
        return int(b_res[1]) - int(a_res[1])

    # Compare two formats by tbr, from high to low
    # If the format has no tbr, it will be placed at the end
    if 'tbr' not in a or a['tbr'] is None:
      return 1
    if 'tbr' not in b or b['tbr'] is None:
      return -1
    return b['tbr'] - a['tbr']

  def _extract_format (self) -> TMdFormats:    
    sorted_raw_formats: list[dict[str, Any]] = sorted(self.metadata['formats'], key=cmp_to_key(self._compare_format))
    # remove format that has no tbr
    # while len(sorted_raw_formats) > 0 and 'tbr' not in sorted_raw_formats[-1]:
    #   sorted_raw_formats.pop()
    
    # extract formats
    formats : TMdFormats = { 'audio': [], 'video': [], 'both': [] }
    for format in sorted_raw_formats:
      has_audio = format.get('acodec', 'none') != 'none' or format.get('format_note', '') == 'Audio'
      has_video = format.get('vcodec', 'none') != 'none'
            
      if 'tbr' not in format:
        LOGGER.debug(f'format {format["format_id"]} skipped, no tbr')
        continue

      audio: Optional[TFormatAudio] = {
        'codec': format.get('acodec', 'none'),
        'ext': format['audio_ext'],
        'format_id': format['format_id'],
        'tbr': format['tbr']
      } if has_audio else None

      video: Optional[TFormatVideo] = {
        'codec': format.get('vcodec', 'none'),
        'ext': format['video_ext'],
        'format_id': format['format_id'],
        'height': int(format['resolution'].split('x')[0]),
        'width': int(format['resolution'].split('x')[1]),
        'tbr': format['tbr']
      } if has_video else None
      
      if has_audio and has_video:
        LOGGER.debug(f'format {format["format_id"]} added to both')
        assert audio is not None and video is not None
        formats['both'].append({
          'format_id': format['format_id'],
          'tbr': format['tbr'],
          'audio': audio,
          'video': video
        })
      if has_audio and not has_video:
        # only accept format that has audio only
        LOGGER.debug(f'format {format["format_id"]} added to audio')
        assert audio is not None
        formats['audio'].append(audio)  
      if has_video:
        LOGGER.debug(f'format {format["format_id"]} added to video')
        assert video is not None
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
  def __init__(self, metadata: dict[str, Any], opts: MetaDataOpt, cid: Optional[int] = None):
    self.bvid: str = metadata['id'].split('_')[0]
    self.cid: Optional[int] = cid
    self.aid: str = bvid_2_aid(self.bvid)
    super().__init__(metadata, opts)    

  def _getSubtitles(self):
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
        'tbr': 0,
        'audio': {
          'codec': 'avc',
          'ext': 'avc',
          'format_id': id,
          'tbr': 0
        },
        'video': {
          'codec': 'aac', 'ext': 'aac',
          'format_id': id,
          'height': 0, 'width': 0,
          'tbr': 0
        }
      })
    
    return formats
# ========================== End Video ========================= #
