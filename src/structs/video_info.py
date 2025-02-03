from __future__ import annotations
from typing import TypedDict, Literal
from colorama import Fore, Style

MediaType = Literal['Video', 'Audio']

# ============ video format ============ #
class BundledFormat:
  """ a type that contains both video and audio format """
  def __init__(self, video: str, audio: str):
    self.video = video
    self.audio = audio
    
  def __eq__(self, __value: object) -> bool:
    if not isinstance(__value, BundledFormat):
      return False
    return self.video == __value.video and self.audio == __value.audio

class TFormatBase (TypedDict):
  format_id : str
  tbr : float

class TFormatFile (TypedDict):
  codec : str
  ext : str
class TFormatVideo (TFormatBase, TFormatFile):
  width : int
  height : int
class TFormatAudio (TFormatBase, TFormatFile):
  pass

class TFormatBoth (TFormatBase):
  video : TFormatVideo
  audio : TFormatAudio
# ============ video format ============ #


# ============ subtitle ============ #
class Subtitle:
  """
    Structure of VideoMetaData subtitle
  """
  def __init__(self, code: str, name: str, isAuto: bool = False):
    self.code = code 
    self.name = name
    self.isAuto= isAuto

  def __str__(self):
    return f'[{self.code}] {self.name} {Fore.LIGHTBLACK_EX}{"(Auto gen)" if self.isAutoGen() else ""}{Style.RESET_ALL}'
  
  def __eq__(self, __value: object) -> bool:
    if not isinstance(__value, Subtitle):
      return False
    if not hasattr(__value, 'code') or not hasattr(__value, 'isAutoGen'):
      return False
    return self.code == __value.code and self.isAutoGen() == __value.isAutoGen()
  
  def __gt__(self, __value: Subtitle) -> bool:
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
  def __init__(self, code: str, name: str, ai_status: int):
    super().__init__(code, name, isAuto=False)
    self.ai_status = ai_status

  def isAutoGen(self) -> bool:
    return self.ai_status != 0
# ============ subtitle ============ #


# ============ stream ============ #
class Stream:
  """ type of FFStream in ffprobe-python module """
  def __init__ (self, data_lines : list[bytes]):
    for line in data_lines:
      v = {str(key): value for key, value, *_ in [line.strip().split(bytes('=', 'UTF-8'))]}
      self.__dict__.update(v)
      
  @property
  def is_audio (self) -> bool:
    return self.__dict__.get('codec_type', None) == 'audio'
# ============ stream ============ #
