from __future__ import annotations

from sys import path as sysPath
sysPath.append('src')

from yt_dlp import YoutubeDL
from enum import Enum

from service.YtDlpHelper import Opts
from service.urlHelper import getSource, UrlSource
from service.fetcher import BiliBiliFetcher
from service.structs import Subtitle

class ErrMessage (Enum):
  NO_PARAM = 'should provide either config or url'
  GET_METADATA_FAILED = 'Get metadata failed'

class MetaData:
  """
    The abstract class of video metadata and playlist metadata
  """
  @staticmethod
  def fetchMetaData(url:str, opts:Opts=Opts()) -> VideoMetaData | PlaylistMetaData:
    # download metadata
    opts = opts.copy()
    opts.quiet = True
    try:
      metadata = YoutubeDL(opts.toParams()).extract_info(
        url = url,
        download = False
      )
    except Exception as e:
      print(e)
      raise Exception(ErrMessage.GET_METADATA_FAILED.value)
    
    if '_type' in metadata and metadata['_type'] == 'playlist':
      print('playlist')
      return PlaylistMetaData(metadata, opts)
    else:
      return VideoMetaData(metadata, opts)

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

class VideoMetaData (MetaData):
  """
    Video metadata
  """
  def __init__(self, metadata, opts:Opts=Opts()):
    super().__init__(metadata)

    # get subtitles
    if getSource(self.url) is UrlSource.BILIBILI:
      # use customer fetcher since hard to get subtitles from bilibili with yt-dlp
      sub, auto_sub = BiliBiliFetcher.getSubtitles(self.id, opts)
    else:
      # get the subtitles from metadata
      sub, auto_sub = self.__extractSubtitles()

    self.subtitles : list[Subtitle] = sub
    self.autoSubtitles : list[Subtitle] = auto_sub

  def isPlaylist(self) -> bool:
    return False
    
  def __extractSubtitles(self) -> (list[Subtitle], list[Subtitle]):
    def restruct_sub_info(sub_info, isAuto:bool=False):
      res = []
      for code, subs in sub_info.items():
        for sub in subs:
          if 'name' in sub:
            res.append(Subtitle(code, sub['name'], isAuto))
            break
      return res
    
    sub = restruct_sub_info(self.metadata['subtitles'])
    auto_sub = []
    if 'automatic_captions' in self.metadata.keys():
      auto_sub = restruct_sub_info(self.metadata['automatic_captions'], True)

    return (sub, auto_sub)

class PlaylistMetaData (MetaData):
  """
    Playlist metadata
  """
  @property
  def playlist_count(self):
    return self.metadata['playlist_count']
  
  def __init__(self, metadata, opts:Opts=Opts()):
    super().__init__(metadata)

    self.videos : list[VideoMetaData] = [
      VideoMetaData(videoMd, opts) for videoMd in self.metadata['entries']
    ]
  
  def isPlaylist(self) -> bool:
    return True
