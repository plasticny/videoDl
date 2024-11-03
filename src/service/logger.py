import logging
from os.path import exists
from os import makedirs, listdir, remove
from datetime import datetime
from json import dump as json_dump

from src.service.fileHelper import LOG_FOLDER_PATH

class Logger:
  def __init__ (self):
    self._prepare()

  def _prepare (self):
    makedirs(LOG_FOLDER_PATH, exist_ok=True)
    logging.basicConfig(
      filename=f'{LOG_FOLDER_PATH}/lyd.log',
      level=logging.DEBUG,
      format='%(asctime)s - %(levelname)s - %(message)s',
      encoding='utf-8'
    )
    
  def info (self, message : str):
    logging.info(message)
    
  def debug (self, message : str):
    logging.debug(message)
    
  def error (self, message : str):
    logging.error(message)
    
  def dump_dict (self, d : dict, name : str = None) -> str:
    """ return name of saved json file """
    if name is None:
      name = str(int(datetime.timestamp(datetime.now()) * 1000000))
    with open(f'{LOG_FOLDER_PATH}/{name}.json', 'w') as f:
      json_dump(d, f, indent=2)
    return name
  
  def clear (self):
    self.info('Clear log files')
    if (not exists(LOG_FOLDER_PATH)):
      return
    for file_nm in listdir(LOG_FOLDER_PATH):
      path = f'{LOG_FOLDER_PATH}/{file_nm}'
      if file_nm == 'lyd.log':
        open(path, 'w').close()
      else:
        remove(path)
