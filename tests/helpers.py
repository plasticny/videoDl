from os import mkdir, listdir, remove
from os.path import exists

OUTPUT_FOLDER_PATH = 'tests/testFiles/output'

def prepare_output_folder ():
  if not exists(OUTPUT_FOLDER_PATH):
    mkdir(OUTPUT_FOLDER_PATH)
  
  for file in listdir(OUTPUT_FOLDER_PATH):
    remove(f'tests/testFiles/output/{file}')

def get_module_full_path (module):
  return f'{module.__module__}.{module.__name__}'