from toml import load as toml_load
from typing import TypedDict, Optional

from src.service.fileHelper import LYD_AUTOFILL_TOML_PATH

# ============== toml structure ============== #
# bottom-up

class TLoginConfig(TypedDict):
  enable: bool
  cookie_path: str
  login_browser: str

class TMediaConfig(TypedDict):
  enable: bool
  val: int

class TFormatOptionConfig(TypedDict):
  enable: bool
  HRLS: bool
  WIN: bool
  
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
  lyd_autofill_config: TLydAutofillConfig = toml_load(f) # type: ignore

def get_login_autofill () -> Optional[tuple[str, str]]:
  # return none if not enable or field is empty
  # else return (cookie_path, login_browser)
  config = lyd_autofill_config['login']
  if not config['enable'] or (config['cookie_path'] == '' and config['login_browser'] == ''):
    return None
  return (config['cookie_path'], config['login_browser'])

def get_lyd_media_autofill () -> Optional[int]:
  config = lyd_autofill_config['media']
  val = config['val']
  return val if config['enable'] and val in [0, 1] else None

def get_lyd_format_option_autofill () -> Optional[dict[str, bool]]:
  if not lyd_autofill_config['format_option']['enable']:
    return None
  return {
    'HRLS': lyd_autofill_config['format_option']['HRLS'],
    'WIN': lyd_autofill_config['format_option']['WIN']
  }

def get_do_write_subtitle_autofill () -> Optional[bool]:
  config = lyd_autofill_config['subtitle']['do_write_subtitle']
  if not config['enable']:
    return None
  return config['val']

def get_sub_lang_autofill () -> Optional[list[str]]:
  config = lyd_autofill_config['subtitle']['sub_lang']
  if not config['enable']:
    return None
  return config['val']

def get_sub_write_mode_autofill () -> Optional[tuple[bool, bool]]:
  """
  Returns:
      tuple[bool, bool]: (embed, burn)
  """
  config = lyd_autofill_config['subtitle']['write_mode']
  if not config['enable']:
    return None
  return config['embed'], config['burn']

def get_output_dir_autofill () -> Optional[str]:
  config = lyd_autofill_config['download']['output_dir']
  if not config['enable'] or config['val'] == '':
    return None
  return config['val']
