import logging
from os.path import dirname as dir, abspath
from os import makedirs
from datetime import datetime
from json import dump as json_dump

class Logger:
  def __init__ (self):
    self.log_dir = self._get_dir(file_path=abspath(__file__))
    self._prepare()

  def _prepare (self):
    makedirs(self.log_dir, exist_ok=True)
    logging.basicConfig(filename=f'{self.log_dir}/lyd.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
  def _get_dir (self, file_path : str) -> str:
    while not (file_path[-3] == 's' and file_path[-2] == 'r' and file_path[-1] == 'c'):
      file_path = dir(file_path)
    return f'{file_path}/logs'
    
  def info (self, message : str):
    logging.info(message)
    
  def debug (self, message : str):
    logging.debug(message)
    
  def dump_dict (self, d : dict, name : str = str(int(datetime.timestamp(datetime.now())))) -> str:
    """ return name of saved json file """
    with open(f'{self.log_dir}/{name}.json', 'w') as f:
      json_dump(d, f, indent=2)
