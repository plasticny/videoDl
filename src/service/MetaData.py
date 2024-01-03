"""
  MetaData of the video or playlist to be downloaded.
  Use MetaData.fetchMetaData to get the metadata of the video or playlist.
"""
from __future__ import annotations

from sys import path as sysPath
sysPath.append('src')

from yt_dlp import YoutubeDL
from contextlib import redirect_stdout
from io import StringIO

from service.YtDlpHelper import Opts
from service.urlHelper import getSource, UrlSource
from service.bilibili import get_bili_subs, get_bili_page_cids, bvid_2_aid
from service.structs import Subtitle

# ========================= funcitons for get the metadata ========================= #
def fetchMetaData(url:str, opts:Opts=Opts()) -> VideoMetaData | PlaylistMetaData:
  """Fetch metadata of the video or playlist to be downloaded"""
  urlSource = getSource(url)

  metadata = __get_basic_metadata(url, urlSource, opts)
  if metadata['_type'] == 'playlist':
    return create_playListMd(metadata, urlSource, opts)
  else:
    return create_videoMd(metadata, urlSource, opts)
  
def fetch_bili_video_metadata (url:str, opts:Opts=Opts()) -> BiliBiliVideoMetaData:
  """
    Fetch metadata function that ensure the video is a bilibili video
  """
# ========================= funcitons for get the metadata ========================= #


# ========================== Abstract MetaData ========================= #
def __get_basic_metadata (url:str, url_source:UrlSource, opts:Opts=Opts()) -> dict:
  opts = opts.copy()
  opts.quiet = True
  opts.extract_flat = True
  # use custom fetcher to get bilibili subtitles
  opts.listSubtitle = not (url_source is UrlSource.BILIBILI)
  try:
    # quiet=True also print subtitle, redirect stdout to hide it
    with redirect_stdout(StringIO()), YoutubeDL(opts.toParams()) as ydl:
      # download basic metadata using yt-dlp
      metadata = ydl.extract_info(url, download = False)
      metadata : dict = ydl.sanitize_info(metadata)
    return metadata
  except Exception as e:
    print(e)
    raise Exception('Get metadata failed')
  
class MetaData:
  """
    The abstract class of video metadata and playlist metadata
  """
  @property
  def title(self) -> str:
    return self.metadata['title']
  @property
  def url(self) -> str:
    return self.metadata['original_url']
  @property
  def id(self) -> str:
    return self.metadata['id']
  
  def __init__ (self, metadata):
    self.metadata : dict = metadata

  def isPlaylist(self) -> bool:
    raise NotImplementedError
# ========================== End Abstract MetaData ========================= #


# ========================== Playlist ========================= #
def create_playListMd(metadata, urlSource:UrlSource, opts:Opts=Opts()) -> PlaylistMetaData:
  """For external use, better use fetchMetaData instead"""
  if urlSource is UrlSource.BILIBILI:
    return BiliBiliPlaylistMetaData(metadata, opts)
  else:
    return PlaylistMetaData(metadata)

class PlaylistMetaData (MetaData):
  """Playlist metadata"""
  @property
  def playlist_count(self) -> int:
    return self.metadata['playlist_count']
  @property
  def video_urls(self) -> list[str]:
    return [v.url for v in self.videos]

  def __init__(self, metadata) -> None:
    super().__init__(metadata)
    self.videos : list[VideoMetaData] = self.fetchVideoMd()
  
  def isPlaylist(self) -> bool:
    return True
  
  def fetchVideoMd(self) -> list[VideoMetaData]:
    res = []
    for entryMd in self.metadata['entries']:
      videoMd = fetchMetaData(entryMd['url'])
      assert not videoMd.isPlaylist()
      res.append(videoMd)
    return res
  
class BiliBiliPlaylistMetaData (PlaylistMetaData):
  """Playlist metadata of bilibili"""
  def __init__(self, metadata, opts:Opts=Opts()):
    self.opts = opts.copy()
    super().__init__(metadata)
    # specify the type of prop videos
    self.videos : list[BiliBiliVideoMetaData] = self.videos

  def fetchVideoMd(self) -> list[BiliBiliVideoMetaData]:
    cids = get_bili_page_cids(self.id, self.opts)

    res = []
    for entryMd, cid in zip(self.metadata['entries'], cids):
      videoMd = fetchMetaData(entryMd['url'], self.opts)
      assert isinstance(videoMd, BiliBiliVideoMetaData)
      videoMd.cid = cid
      res.append(videoMd)
    return res
# ========================== End Playlist ========================= #


# ========================== Video ========================= #
def create_videoMd(metadata, urlSource:UrlSource, opts:Opts=Opts()) -> VideoMetaData:
  """For external use, better use fetchMetaData instead"""
  if urlSource is UrlSource.BILIBILI:
    return BiliBiliVideoMetaData(metadata, opts = opts)
  else:
    return VideoMetaData(metadata)

class VideoMetaData (MetaData):
  """Video metadata"""
  @property
  def subtitles(self) -> list[Subtitle]:
    if self._sub is None:
      self.getSubtitles()
    return self._sub
  @property
  def autoSubtitles(self) -> list[Subtitle]:
    if self._auto_sub is None:
      self.getSubtitles()
    return self._auto_sub
  @property
  def formats(self) -> list[dict]:
    if self._format is not None:
      return self._format

    format_dict = {} 
    for format in self.metadata['formats']:
      if format['audio_ext'] == 'none' and format['video_ext'] == 'none':
        continue
      key = hash((format['audio_ext'], format['video_ext']))
      if key not in format_dict:
        format_dict[key] = {"audio": format["audio_ext"], "video": format["video_ext"]} 
    
    self._format = list(format_dict.values())
    return self._format
  
  @property
  def audio_formats(self) -> list[dict]:
    return [f['audio'] for f in self.formats if f['audio'] != 'none']
  @property
  def video_formats(self) -> list[dict]:
    return [f['video'] for f in self.formats if f['video'] != 'none']
  
  def __init__(self, metadata):
    super().__init__(metadata)

    # will be initialized in getSubtitles when property is called
    self._sub : list[Subtitle] = None
    self._auto_sub : list[Subtitle] = None
    self._format : list[dict] = None

  def isPlaylist(self) -> bool:
    return False
    
  def getSubtitles(self) -> None:
    """
      Used to assign value to `self._sub` and `self._auto_sub`\n
      `self._sub` and `self._auto_sub` should not be None after this function is called
    """
    def restruct_sub_info(sub_info:dict, isAuto:bool=False):
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
    
    self._sub = restruct_sub_info(self.metadata['subtitles'])
    if 'automatic_captions' in self.metadata.keys():
      self._auto_sub = restruct_sub_info(self.metadata['automatic_captions'], True)
    else:
      self._auto_sub = []

class BiliBiliVideoMetaData (VideoMetaData):
  """
    Video metadata of bilibili
  """
  def __init__(self, metadata, opts: Opts = Opts()):
    self.opts = opts.copy()
    super().__init__(metadata)
    
    self.bvid : str = self.id.split('_')[0]
    self.cid : str = None # set in BiliBiliPlaylistMetaData.fetchVideoMd if it is a page in playlist
    self.aid : str = bvid_2_aid(self.bvid)

  def getSubtitles(self) -> None:
    sub, auto_sub = get_bili_subs(self.bvid, self.opts, self.cid)
    self._sub = sub
    self._auto_sub = auto_sub
    self.opts = None # opts is not needed anymore, release memory
# ========================== End Video ========================= #
