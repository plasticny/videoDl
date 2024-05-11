from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from tests.helpers import OUTPUT_FOLDER_PATH

from src.service.logger import Logger


@patch('src.service.logger.Logger._prepare')
def test_get_dir (prepare_mock : Mock):
  prepare_mock.return_value = None
  dir = Logger()._get_dir('/home/user/lyd/src/service/logger.py')
  assert dir == '/home/user/lyd/src/logs'

@patch('src.service.logger.Logger._get_dir')
@patch('src.service.logger.logging.info')
def test_info (info_mock : Mock, get_dir_mock : Mock):
  get_dir_mock.return_value = OUTPUT_FOLDER_PATH
  logger = Logger()
  logger.info('info message')
  assert info_mock.call_count == 1
  assert info_mock.call_args[0][0] == 'info message'

@patch('src.service.logger.Logger._get_dir')
@patch('src.service.logger.logging.debug')
def test_debug (debug_mock : Mock, get_dir_mock : Mock):
  get_dir_mock.return_value = OUTPUT_FOLDER_PATH
  logger = Logger()
  logger.debug('debug message')
  assert debug_mock.call_count == 1
  assert debug_mock.call_args[0][0] == 'debug message'

@patch('src.service.logger.Logger._get_dir')
@patch('src.service.logger.json_dump')
def test_dump_dict (json_dump_mock : Mock, get_dir_mock : Mock):
  get_dir_mock.return_value = OUTPUT_FOLDER_PATH
  d = {'key': 'value'}
  logger = Logger()
  logger.dump_dict(d)
  assert json_dump_mock.call_count == 1
  assert json_dump_mock.call_args[0][0] == d
