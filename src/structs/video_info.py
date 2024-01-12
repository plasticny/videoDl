from __future__ import annotations
from typing import TypedDict
from colorama import Fore, Style


# ============ video format ============ #
class BundledFormat:
  """ a type that contains both video and audio format """
  def __init__(self, video:str=None, audio:str=None):
    self.video : str = video
    self.audio : str = audio

class TFormatDesc (TypedDict):
  codec : str
  ext : str

class TFormatBase (TypedDict):
  format_id : str
  tsr : float
class TFormatVideo (TFormatBase):
  video : TFormatDesc
class TFormatAudio (TFormatBase):
  audio : TFormatDesc
class TFormatBoth (TFormatVideo, TFormatAudio):
  pass
# ============ video format ============ #


# ============ subtitle ============ #
class Subtitle:
  """
    Structure of VideoMetaData subtitle
  """
  def __init__(self, code, name, isAuto=False):
    self.code : str = code
    self.name : str = name
    self.isAuto : bool = isAuto

  def __str__(self):
    return f'[{self.code}] {self.name} {Fore.LIGHTBLACK_EX}{"(Auto gen)" if self.isAutoGen() else ""}{Style.RESET_ALL}'
  
  def __eq__(self, __value) -> bool:
    if not hasattr(__value, 'code') or not hasattr(__value, 'isAutoGen'):
      return False
    return self.code == __value.code and self.isAutoGen() == __value.isAutoGen()
  
  def __gt__(self, __value) -> bool:
    if self.__eq__(__value):
      return False
    
    assert hasattr(__value, 'name') and hasattr(__value, 'isAutoGen')
    if self.isAutoGen() == __value.isAutoGen():
      return self.name > __value.name
    return self.isAutoGen()
  
  def __hash__(self) -> int:
    return hash(f'{self.code}{self.isAutoGen()}')
  
  def isAutoGen(self) -> bool:
    return self.isAuto
  
class BiliBiliSubtitle(Subtitle):
  """
    Structure of BiliBiliVideoMetaData subtitle

    Metadata of bilibili video does not distinguish between auto and non-auto subtitle\n
    So isAuto should always be False, and use ai_status for internal distinction
  """
  def __init__(self, code, name, ai_status):
    super().__init__(code, name, isAuto=False)
    self.ai_status = ai_status

  def isAutoGen(self) -> bool:
    return self.ai_status != 0
# ============ subtitle ============ #
