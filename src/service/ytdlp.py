from os import popen
from json import loads
from subprocess import run as run_cmd
from typing import TypedDict, Callable, Optional, Any, cast

from src.service.logger import Logger
from src.service.fileHelper import FFMPEG_FOLDER_PATH, YT_DLP_PATH

from src.structs.option import TOpt

class _Params (TypedDict):
  cookiefile: Optional[str]
  extract_flat: Optional[bool]
  format: Optional[str]
  sorting: Optional[str]
  login_browser: Optional[str]
  outtmpl: Optional[str]
  overwrites: Optional[bool]
  paths: Optional[dict[str, str]]
  quiet: Optional[bool]
  skip_download: Optional[bool]
  subtitleslangs: Optional[list[str]]
  writeautomaticsub: Optional[bool]
  writesubtitles: Optional[bool]

class Ytdlp:
  @staticmethod
  def upgrade () -> None:
    run_cmd(f'{YT_DLP_PATH} -U')
  
  def __init__ (self, opt: TOpt = {}) -> None:
    self.params: _Params = opt.copy() # type: ignore
    self.base_cmd = self._build_base_cmd()
    self.logger = Logger()

    self.logger.info(f'Ytdlp instance created')
    self.logger.info(f'params: {self.params}')
      
  def _build_base_cmd (self) -> str:
    has_value : Callable[[str], bool] = lambda x : self.params.get(x, None) is not None
    is_true : Callable[[str], bool] = lambda x : self.params.get(x, False)

    return \
      f'{YT_DLP_PATH} ' + \
      f'--ffmpeg-location {FFMPEG_FOLDER_PATH} ' + \
      (f'--cookies {self.params["cookiefile"]} '                                  if has_value('cookiefile') else '') + \
      (f'--cookies-from-browser {self.params["login_browser"]} '                  if has_value('login_browser') else '') + \
      (f'--flat-playlist '                                                        if is_true('extract_flat') else '') + \
      (f'--format {self.params["format"]} '                                       if has_value('format') else '') + \
      (f'-S {self.params["sorting"]} '                                            if has_value('sorting') else '') + \
      (f'--force-overwrite '                                                      if is_true('overwrites') else '') + \
      (f'-q '                                                                     if is_true('quiet') else '') + \
      (f'--skip-download '                                                        if is_true('skip_download') else '') + \
      (f'--sub-lang {",".join(cast(list[str], self.params["subtitleslangs"]))} '  if has_value('subtitleslangs') else '') + \
      (f'-P {cast(dict[str, str], self.params["paths"])["home"]} '                if has_value('paths') else '') + \
      (f'--write-sub '                                                            if is_true('writesubtitles') else '') + \
      (f'--write-auto-sub '                                                       if is_true('writeautomaticsub') else '') + \
      (f'-o {self.params["outtmpl"]} '                                            if has_value('outtmpl') else '')
      
  def extract_info (self, url: str) -> dict[str, Any]:
    # if no --list-subs, it cannot find some subtitles
    cmd = f'{self.base_cmd} -J --list-subs {url}'
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
