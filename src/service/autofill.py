from toml import load as toml_load
from os import getcwd
from typing import TypedDict


class TLoginConfig(TypedDict):
  enable: bool
  cookit_path : dict[str, str]

class TFormatConfig(TypedDict):
  enable: bool
  prefered_format: int
  
class TSubtitleConfig(TypedDict):
  enable: bool
  do_write_subtitle: bool
  sub_lang: list[str]
  embed: bool
  burn: bool
  
class TDownloadConfig(TypedDict):
  enable: bool
  output_path: str

class TLydAutofillConfig(TypedDict):  
  login: TLoginConfig
  format: TFormatConfig
  subtitle: TSubtitleConfig
  download: TDownloadConfig


with open(f'{getcwd()}/src/lyd_autofill.toml', 'r') as f:
  lyd_autofill_config : TLydAutofillConfig = toml_load(f)


def get_login_autofill (url:str) -> str:
  if not lyd_autofill_config['login']['enable']:
    return None
    
  for key, value in lyd_autofill_config['login']['cookit_path'].items():
    if key in url and value != '':
      return value
  return None

def get_lyd_format_autofill () -> int:
  if not lyd_autofill_config['format']['enable']:
    return None
  
  prefered_format = lyd_autofill_config['format']['prefered_format']
  if prefered_format == 0 or prefered_format == 1:
    return prefered_format
  return None