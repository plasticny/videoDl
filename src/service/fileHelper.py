from os.path import exists, dirname, abspath
from os import mkdir, remove, listdir, environ

ENV = environ.get('RUNTIME_ENV', 'dev')

def path_variables () -> dict[str, str]:
  if ENV == 'dev':
    root_path = dirname(abspath(__file__)).split('\\src')[0]
    return {
      'ROOT_PATH': root_path,
      'TEMP_FOLDER_PATH': f'{root_path}\\temp',
      'FFMPEG_FOLDER_PATH': f'{root_path}\\src\\ffmpeg',
      'LYD_AUTOFILL_TOML_PATH': f'{root_path}\\src\\lyd_autofill.toml',
      'YT_DLP_PATH': f'{root_path}\\src\\yt-dlp.exe',
      'LOG_FOLDER_PATH': f'{root_path}\\src\\logs'
    }
  elif ENV == 'prod':
    root_path = dirname(abspath(__file__)).split('\\src')[0]
    return {
      'ROOT_PATH': dirname(abspath(__file__)).split('\\src')[0],
      'TEMP_FOLDER_PATH': f'{root_path}\\temp',
      'FFMPEG_FOLDER_PATH': f'{root_path}',
      'LYD_AUTOFILL_TOML_PATH': f'{root_path}\\lyd_autofill.toml',
      'YT_DLP_PATH': f'{root_path}\\yt-dlp.exe',
      'LOG_FOLDER_PATH': f'{root_path}\\logs'
    }
  raise Exception('Invalid ENV')
PATH_VARIABLES = path_variables()

ROOT_PATH = PATH_VARIABLES['ROOT_PATH']
TEMP_FOLDER_PATH = PATH_VARIABLES['TEMP_FOLDER_PATH']
FFMPEG_FOLDER_PATH = PATH_VARIABLES['FFMPEG_FOLDER_PATH']
LYD_AUTOFILL_TOML_PATH = PATH_VARIABLES['LYD_AUTOFILL_TOML_PATH']
YT_DLP_PATH = PATH_VARIABLES['YT_DLP_PATH']
LOG_FOLDER_PATH = PATH_VARIABLES['LOG_FOLDER_PATH']

def perpare_temp_folder():
  """
    prepare a empty temp folder
  """
  if not exists(TEMP_FOLDER_PATH):
    mkdir(TEMP_FOLDER_PATH)
  clear_temp_folder()

def clear_temp_folder():
  """
    clear the temp folder
  """
  for nm in listdir(TEMP_FOLDER_PATH):
    remove(f'{TEMP_FOLDER_PATH}\\{nm}')