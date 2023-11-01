from __future__ import annotations

from enum import Enum
from json import loads as jsonLoads

from dlConfig import dlConfig
from service.commandUtils import runCommand, YT_EXEC
from service.YtDlpHelper import CommandConverter

class ErrMessage (Enum):
  NO_PARAM = 'should provide either config or url'
  GET_METADATA_FAILED = 'Get metadata failed'

class TYPE (Enum):
  VIDEO = 'video'
  PLAYLIST = 'playlist'

class MetaData:
  @staticmethod
  def fetchMetaData(config:dlConfig=None, url:str=None) -> VideoMetaData | PlaylistMetaData:
    # check parameter
    if config == None and url == None:
      raise Exception(ErrMessage.NO_PARAM.value)
    
    # set up config
    if config == None:
      config = dlConfig()
      config.url = url
    cc = CommandConverter(config)

    # download metadata
    result = runCommand(
      execCommand=YT_EXEC, 
      paramCommands=[
        cc.url,
        cc.skipDownload,
        cc.getMetaData
      ],
      catch_stdout=True
    )

    if result.returncode != 0:
      raise Exception(ErrMessage.GET_METADATA_FAILED.value)

    # parse metadata
    metadata = jsonLoads(result.stdout)
    if metadata['_type'] == TYPE.VIDEO.value:
      return VideoMetaData(metadata)
    elif metadata['_type'] == TYPE.PLAYLIST.value:
      return PlaylistMetaData(metadata)

  @property
  def title(self):
    return self.metadata['title']
  @property
  def _type(self):
    return self.metadata['_type']
  @property
  def url(self):
    return self.metadata['original_url']
  
  def __init__ (self, metadata):
    self.metadata = metadata

  def getVideos(self) -> list[VideoMetaData]:
    raise NotImplementedError

class VideoMetaData (MetaData):
  def getVideos(self) -> list[VideoMetaData]:
    return [self]

class PlaylistMetaData (MetaData):
  @property
  def playlist_count(self):
    return self.metadata['playlist_count']
  
  def getVideos(self) -> list[VideoMetaData]:
    videos = []
    for videoMd in self.metadata['entries']:
      videos.append(VideoMetaData(videoMd))
    return videos