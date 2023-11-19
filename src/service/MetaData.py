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
from service.fetcher import BiliBiliFetcher
from service.structs import Subtitle

# ========================== Abstract MetaData ========================= #
def fetchMetaData(url:str, opts:Opts=Opts()) -> VideoMetaData | PlaylistMetaData:
  """Fetch metadata of the video or playlist to be downloaded"""
  urlSource = getSource(url)

  opts = opts.copy()
  opts.quiet = True
  opts.extract_flat = True
  # use custom fetcher to get bilibili subtitles
  opts.listSubtitle = not (urlSource is UrlSource.BILIBILI)
  try:
    # quiet=True also print subtitle, redirect stdout to hide it
    with redirect_stdout(StringIO()), YoutubeDL(opts.toParams()) as ydl:
      # download basic metadata using yt-dlp
      metadata = ydl.extract_info(url, download = False)
      metadata = ydl.sanitize_info(metadata)
  except Exception as e:
    print(e)
    raise Exception('Get metadata failed')
  
  if metadata['_type'] == 'playlist':
    return create_playListMd(metadata, urlSource, opts)
  else:
    return create_videoMd(metadata, urlSource, opts)
  
class MetaData:
  """
    The abstract class of video metadata and playlist metadata
  """
  @property
  def title(self):
    return self.metadata['title']
  @property
  def url(self):
    return self.metadata['original_url']
  @property
  def id(self):
    return self.metadata['id']
  
  def __init__ (self, metadata):
    self.metadata = metadata

  def isPlaylist(self) -> bool:
    raise NotImplementedError
# ========================== End Abstract MetaData ========================= #

# ========================== Playlist ========================= #
def create_playListMd(metadata, urlSource:UrlSource, opts:Opts=Opts()) -> PlaylistMetaData:
  """
    Depends on the source, return different type of playlist metadata\n
    For external use, better use fetchMetaData instead

    Args:
      metadata: the metadata dict fetched in fetchMetaData
  """
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

  def fetchVideoMd(self) -> list[BiliBiliVideoMetaData]:
    cids = BiliBiliFetcher.get_page_cids(self.id, self.opts)

    res = []
    for idx, entryMd in enumerate(self.metadata['entries']):
      videoMd = fetchMetaData(entryMd['url'], self.opts)
      assert isinstance(videoMd, BiliBiliVideoMetaData)
      videoMd.cid = cids[idx]
      res.append(videoMd)
    return res
# ========================== End Playlist ========================= #

# ========================== Video ========================= #
def create_videoMd(metadata, urlSource:UrlSource, opts:Opts=Opts()) -> VideoMetaData:
  """
    Depends on the source, return different type of video metadata\n
    For external use, better use fetchMetaData instead

    Args:
      metadata: the metadata dict fetched in fetchMetaData
  """
  if urlSource is UrlSource.BILIBILI:
    return BiliBiliVideoMetaData(metadata, opts)
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

  def __init__(self, metadata):
    super().__init__(metadata)

    # will be initialized in getSubtitles when property is called
    self._sub : list[Subtitle] = None
    self._auto_sub : list[Subtitle] = None

  def isPlaylist(self) -> bool:
    return False
    
  def getSubtitles(self) -> None:
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

class BiliBiliVideoMetaData (VideoMetaData):
  """
    Video metadata of bilibili

    properties:
      `cid`: useful when the video is a page in playlist, set in BiliBiliPlaylistMetaData.fetchVideoMd
  """
  def __init__(self, metadata, opts: Opts = Opts()):
    self.opts = opts.copy()
    self.cid = None
    super().__init__(metadata)

  def getSubtitles(self) -> None:
    sub, auto_sub =  BiliBiliFetcher.getSubtitles(self.id, self.opts, self.cid)
    self._sub = sub
    self._auto_sub = auto_sub
# ========================== End Video ========================= #