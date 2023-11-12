from __future__ import annotations
import copy

class Opts:
  def __init__(self) -> None:
    self.opts = {}
    self.reset()

  def __eq__(self, other: Opts) -> bool:
    return self.opts == other.opts

  def copy(self) -> Opts:
    return copy.deepcopy(self)
  def reset(self) -> Opts:
    self.opts = {
      # output
      'outtmpl': None,
      'paths': {},
      # format
      'format': None,
      'merge_output_format': None,
      # subtitle
      'writeautomaticsub': None,
      'writesubtitles': None,
      'subtitleslangs': None,
      # cookie
      'cookiefile': None,
      # list
      'listformats': None,
      'listsubtitles': None,
      # others
      'skip_download': None,
      'quiet': None,
      'overwrites': None,
      'ffmpeg_location': 'ffmpeg',

      # some params that not belong to yt_dlp
      'not_yt_dlp': {
        'embedSubtitle': None,
        'burnSubtitle': None
      }
    }
    return self

  def toParams(self) -> dict:
    ret_opts = self.opts.copy()
    del ret_opts['not_yt_dlp']
    return ret_opts

  # ========= fast getter and setter function for the opts params =========
  """ output """
  @property
  def outputName (self) -> str:
    return self.opts['outtmpl']
  @outputName.setter
  def outputName (self, val:str) -> None:
    self.opts['outtmpl'] = val
  
  @property
  def outputDir (self) -> str:
    if 'home' not in self.opts['paths']:
      return None
    return self.opts['paths']['home']
  @outputDir.setter
  def outputDir (self,val:str) -> None:
    self.opts['paths']['home'] = val
  
  """ format """
  @property
  def format (self) -> str:
    return self.opts['format']
  @format.setter
  def format (self, val:str) -> None:
    self.opts['format'] = val

  """ subtitle """
  @property
  def writeAutomaticSub (self) -> bool:
    return self.opts['writeautomaticsub']
  @writeAutomaticSub.setter
  def writeAutomaticSub (self, val:bool = True) -> None:
    self.opts['writeautomaticsub'] = val
  
  @property
  def writeSubtitles (self) -> bool:
    return self.opts['writesubtitles']
  @writeSubtitles.setter
  def writeSubtitles (self, val:bool = True) -> None:
    self.opts['writesubtitles'] = val
  
  @property
  def subtitlesLang (self) -> str:
    sl = self.opts['subtitleslangs']
    if sl is None or len(sl) == 0:
      return None
    return sl[0]
  @subtitlesLang.setter
  def subtitlesLang (self, val:str) -> None:
    self.opts['subtitleslangs'] = [val]
  
  @property
  def embedSubtitle (self) -> bool:
    return self.opts['not_yt_dlp']['embedSubtitle']
  @embedSubtitle.setter
  def embedSubtitle (self, val:bool = True) -> None:
    self.opts['not_yt_dlp']['embedSubtitle'] = val
  
  @property
  def burnSubtitle (self) -> bool:
    return self.opts['not_yt_dlp']['burnSubtitle']
  @burnSubtitle.setter
  def burnSubtitle (self, val:bool = True) -> None:
    self.opts['not_yt_dlp']['burnSubtitle'] = val
  
  """ cookie """
  @property
  def cookieFile (self) -> str:
    return self.opts['cookiefile']
  @cookieFile.setter
  def cookieFile (self, val:str) -> None:
    self.opts['cookiefile'] = val
  
  """ list info """
  @property
  def listFormats (self) -> bool:
    return self.opts['listformats']
  @listFormats.setter
  def listFormats (self, val:bool = True) -> None:
    self.opts['listformats'] = val
  
  @property
  def listSubtitle (self) -> bool:
    return self.opts['listsubtitles']
  @listSubtitle.setter
  def listSubtitle (self, val:bool = True) -> None:
    self.opts['listsubtitles'] = val

  """ others """
  @property
  def skip_download (self) -> bool:
    return self.opts['skip_download']
  @skip_download.setter
  def skip_download (self, val:bool = True) -> None:
    self.opts['skip_download'] = val
  
  @property
  def quiet (self) -> bool:
    return self.opts['quiet']
  @quiet.setter
  def quiet (self, val:bool = True) -> None:
    self.opts['quiet'] = val
  
  @property
  def overwrites (self) -> bool:
    return self.opts['overwrites']
  @overwrites.setter
  def overwrites (self, val:bool = True) -> None:
    self.opts['overwrites'] = val
  
  @property
  def ffmpeg_location (self) -> str:
    return self.opts['ffmpeg_location']
  @ffmpeg_location.setter
  def ffmpeg_location (self, val:str) -> None:
    self.opts['ffmpeg_location'] = val
  # ========= END fast getter and setter function for the opts params END =========