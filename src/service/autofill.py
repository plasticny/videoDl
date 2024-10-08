from toml import load as toml_load
from typing import TypedDict, Union, Optional

from src.service.fileHelper import LYD_AUTOFILL_TOML_PATH

# ============== toml structure ============== #
# bottom-up

class TLoginConfig(TypedDict):
  enable: bool
  cookie_path : dict[str, str]

class TMediaConfig(TypedDict):
  enable: bool
  val: int

class TFormatOptionConfig(TypedDict):
  enable: bool
  HRLS: bool
  AHEV: bool
  AAV1: bool
  
class TDoWriteSubtitle(TypedDict):
  enable: bool
  val: bool
class TSubLang(TypedDict):
  enable: bool
  val: list[str]
class TSubWriteMode(TypedDict):
  enable: bool
  embed: bool
  burn: bool
class TSubtitleConfig(TypedDict):
  do_write_subtitle: TDoWriteSubtitle
  sub_lang: TSubLang
  write_mode: TSubWriteMode

class TOutputDir(TypedDict):
  enable: bool
  val: str
class TDownloadConfig(TypedDict):
  output_dir: TOutputDir

class TLydAutofillConfig(TypedDict):  
  login: TLoginConfig
  media: TMediaConfig
  format_option: TFormatOptionConfig
  subtitle: TSubtitleConfig
  download: TDownloadConfig
# ============== toml structure ============== #

with open(LYD_AUTOFILL_TOML_PATH, 'r') as f:
  lyd_autofill_config : TLydAutofillConfig = toml_load(f)

def get_login_autofill (url:str) -> str:
  config = lyd_autofill_config['login']
  if not config['enable']:
    return None
  
  for key, value in config['cookie_path'].items():
    if key in url and value != '':
      return value
  return None

def get_lyd_media_autofill () -> Union[str, None]:
  config = lyd_autofill_config['media']
  val = config['val']
  return val if config['enable'] and val in [0, 1] else None

def get_lyd_format_option_autofill () -> Optional[dict]:
  if not lyd_autofill_config['format_option']['enable']:
    return None
  
  res = lyd_autofill_config['format_option'].copy()
  res.pop('enable')
  return res

def get_do_write_subtitle_autofill () -> bool:
  config = lyd_autofill_config['subtitle']['do_write_subtitle']
  if not config['enable']:
    return None
  return config['val']

def get_sub_lang_autofill () -> list[str]:
  config = lyd_autofill_config['subtitle']['sub_lang']
  if not config['enable']:
    return None
  return config['val']

def get_sub_write_mode_autofill () -> tuple[bool, bool]:
  """
  Returns:
      tuple[bool, bool]: (embed, burn)
  """
  config = lyd_autofill_config['subtitle']['write_mode']
  if not config['enable']:
    return None
  return config['embed'], config['burn']

def get_output_dir_autofill () -> str:
  config = lyd_autofill_config['download']['output_dir']
  if not config['enable'] or config['val'] == '':
    return None
  return config['val']
