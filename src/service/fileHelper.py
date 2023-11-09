from os.path import exists
from os import mkdir, remove, listdir

"""
folder for storing temp file when downlaoding
"""
TEMP_FOLDER_PATH = 'temp'

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