from os import popen
from json import loads
from typing import TypedDict, TypeVar, Union, Callable
from subprocess import run as run_cmd

from src.service.logger import Logger

from src.structs.option import IOpt

_T = TypeVar('_T')
_V = Union[_T, None]
EXE_NM = 'src\\yt-dlp_min.exe'

class _Params (TypedDict):
  cookiefile: _V[str]
  extract_flat: _V[bool]
  format: _V[str]
  outtmpl: _V[str]
  overwrites: _V[bool]
  paths: _V[dict[str, str]]
  quiet: _V[bool]
  skip_download: _V[bool]
  subtitleslangs: _V[list[str]]
  writeautomaticsub: _V[bool]
  writesubtitles: _V[bool]

class Ytdlp:
  @staticmethod
  def upgrade () -> None:
    popen(f'{EXE_NM} -U')
  
  def __init__ (self, opt: IOpt) -> None:
    self.params: _Params = {}
    for k, v in opt.items():
      self.params[k] = v
    
    self.base_cmd = self._build_base_cmd()
    
    self.logger = Logger()
      
  def _build_base_cmd (self) -> str:
    has_value : Callable[[str], bool] = lambda x : self.params.get(x, None) is not None
    is_true : Callable[[str], bool] = lambda x : self.params.get(x, False)
    
    return \
      f'{EXE_NM} ' + \
      (f'--cookies {self.params["cookiefile"]} '                 if has_value('cookiefile') else '') + \
      (f'--flat-playlist '                                       if is_true('extract_flat') else '') + \
      (f'--format {self.params["format"]} '                      if has_value('format') else '') + \
      (f'--force-overwrite '                                     if is_true('overwrites') else '') + \
      (f'-q '                                                    if is_true('quiet') else '') + \
      (f'--skip-download '                                       if is_true('skip_download') else '') + \
      (f'--write-sub '                                           if is_true('writesubtitles') else '') + \
      (f'--write-auto-sub '                                      if is_true('writeautomaticsub') else '') + \
      (f'--sub-lang {",".join(self.params["subtitleslangs"])} '  if has_value('subtitleslangs')else '') + \
      (f'-P {self.params["paths"]["home"]} '                     if has_value('paths') else '') + \
      (f'-o {self.params["outtmpl"]} '                           if has_value('outtmpl') else '')
      
  def extract_info (self, url: str) -> dict:
    # if no --list-subs, it cannot find some subtitles
    cmd = f'{self.base_cmd} -J --list-subs -q {url}'
    self.logger.debug(f"Running command: {cmd}")
    
    # since --list-subs is used, only the last line of the output is the metadata (\n is the last char)
    info = loads(popen(cmd).read().split('\n')[-2])
    json_name = self.logger.dump_dict(info)
    self.logger.debug(f'Metadata of {url} has been saved to {json_name}.json')

    return info
  
  def download (self, url: str) -> None:
    cmd = f'{self.base_cmd} {url}'
    self.logger.debug(f"Running command: {cmd}")
    run_cmd(cmd)
