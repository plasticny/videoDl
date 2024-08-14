from os.path import exists, dirname, abspath
from os import mkdir, remove, listdir, environ

ENV = environ['RUNTIME_ENV'] if 'RUNTIME_ENV' in environ else 'dev'

if ENV == 'dev':
  ROOT_PATH = dirname(abspath(__file__)).split('\\service')[0]
  TEMP_FOLDER_PATH = f'{ROOT_PATH}\\..\\temp'
  FFMPEG_FOLDER_PATH = f'{ROOT_PATH}\\ffmpeg'
elif ENV == 'prod':
  ROOT_PATH = dirname(abspath(__file__)).split('\\src')[0]
  TEMP_FOLDER_PATH = f'{ROOT_PATH}\\temp'
  FFMPEG_FOLDER_PATH = f'{ROOT_PATH}'
  
LYD_AUTOFILL_TOML_PATH = f'{ROOT_PATH}\\lyd_autofill.toml'


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