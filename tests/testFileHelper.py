from os import mkdir, listdir, remove
from os.path import exists

def prepare_output_folder ():
  if not exists('tests/testFiles/output'):
    mkdir('tests/testFiles/output')
  
  for file in listdir('tests/testFiles/output'):
    remove(f'tests/testFiles/output/{file}')