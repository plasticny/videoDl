from __future__ import annotations

from sys import path as sysPath
sysPath.append('src')

from yt_dlp import YoutubeDL
from enum import Enum

from service.YtDlpHelper import Opts

class ErrMessage (Enum):
  NO_PARAM = 'should provide either config or url'
  GET_METADATA_FAILED = 'Get metadata failed'

class MetaData:
  @staticmethod
  def fetchMetaData(url:str) -> VideoMetaData | PlaylistMetaData:
    # download metadata
    opts = Opts()
    opts.quiet()
    try:
      metadata = YoutubeDL(opts()).extract_info(
        url = url,
        download = False
      )
    except Exception as e:
      print(e)
      raise Exception(ErrMessage.GET_METADATA_FAILED.value)
    
    try:
      if metadata['_type'] == 'playlist':
        return PlaylistMetaData(metadata)
    except:
      return VideoMetaData(metadata)

  @property
  def title(self):
    return self.metadata['title']
  @property
  def url(self):
    return self.metadata['original_url']
  
  def __init__ (self, metadata):
    self.metadata = metadata

  def isPlaylist(self) -> bool:
    raise NotImplementedError

class VideoMetaData (MetaData):
  def isPlaylist(self) -> bool:
    return False

class PlaylistMetaData (MetaData):
  @property
  def playlist_count(self):
    return self.metadata['playlist_count']
  
  def isPlaylist(self) -> bool:
    return True

  def getVideos(self) -> list[VideoMetaData]:
    videos = []
    for videoMd in self.metadata['entries']:
      videos.append(VideoMetaData(videoMd))
    return videos