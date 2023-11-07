from __future__ import annotations
import copy

class Opts:
  def __init__(self) -> None:
    self.opts = {}
    self.reset()

  def __call__(self) -> dict:
    return self.opts
  def __eq__(self, other: Opts) -> bool:
    return self.opts == other.opts

    # === codes for deep comparison, useless now ===
    # def sameItem(a, b) -> bool:
    #   if a is None and b is None:
    #     return True
    #   if (a is None) != (b is None):
    #     return False
    #   if isinstance(a, dict) and not sameDict(a, b):
    #     return False
    #   if isinstance(a, list) and not sameList(a, b):
    #     return False
    #   if a != b:
    #     return False
    #   return True

    # def sameDict(a:dict, b:dict) -> bool:
    #   if len(a) != len(b):
    #     return False
    #   for key in a.keys():
    #     if not(key in b) or not sameItem(a[key], b[key]):
    #       return False
    #   return True
            
    # def sameList(a:list, b:list) -> bool:
    #   if len(a) != len(b):
    #     return False
    #   for a_v, b_v in zip(a, b):
    #     if not sameItem(a_v, b_v):
    #       return False
    #   return True
    
    # for key in self.opts:
    #   # suppose self and other must have the same keys
    #   if not sameItem(self.opts[key], other.opts[key]):
    #     return False
    # return True

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
      # postprocessor
      'postprocessors': [],
      # others
      'skip_download': None,
      'quiet': None,
      'overwrites': None
    }
    return self

  # output
  def outputName (self, val:str) -> Opts:
    self.opts['outtmpl'] = val
    return self
  def outputDir (self,val:str) -> Opts:
    self.opts['paths']['home'] = val
    return self
  
  # format
  def format (self, val:str) -> Opts:
    self.opts['format'] = val
    return self
  def mergeFormat (self, val:str) -> Opts:
    self.opts['merge_output_format'] = val
    return self
  
  # subtitle
  def writeAutomaticSub (self, val:bool = True) -> Opts:
    self.opts['writeautomaticsub'] = val
    return self
  def writeSubtitles (self, val:bool = True) -> Opts:
    self.opts['writesubtitles'] = val
    return self
  def subtitlesLang (self, val:str) -> Opts:
    self.opts['subtitleslangs'] = [val]
    return self
  def embedSubtitle (self, val:bool = True) -> Opts:
    KEY = 'FFmpegEmbedSubtitle'
    if val:
      self.opts['postprocessors'].append({'key': KEY})
    else:
      self.opts['postprocessors'] = list(
        filter(lambda pp: pp['key'] != KEY, self.opts['postprocessors'])
      )
    return self
  
  # cookie
  def cookieFile (self, val:str) -> Opts:
    self.opts['cookiefile'] = val
    return self
  
  # list
  def listFormats (self, val:bool = True) -> Opts:
    self.opts['listformats'] = val
    return self
  def listSubtitle (self, val:bool = True) -> Opts:
    self.opts['listsubtitles'] = val
    return self

  # others
  def skip_download (self, val:bool = True) -> Opts:
    self.opts['skip_download'] = val
    return self
  def quiet (self, val:bool = True) -> Opts:
    self.opts['quiet'] = val
    return self
  def overwrites (self, val:bool = True) -> Opts:
    self.opts['overwrites'] = val
    return self