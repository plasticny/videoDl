from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from os import listdir

from tests.helpers import OUTPUT_FOLDER_PATH, prepare_output_folder

from src.service.logger import Logger


@patch('src.service.logger.LOG_FOLDER_PATH', OUTPUT_FOLDER_PATH)
@patch('src.service.logger.logging.info')
def test_info (info_mock : Mock):
  logger = Logger()
  logger.info('info message')
  assert info_mock.call_count == 1
  assert info_mock.call_args[0][0] == 'info message'

@patch('src.service.logger.LOG_FOLDER_PATH', OUTPUT_FOLDER_PATH)
@patch('src.service.logger.logging.debug')
def test_debug (debug_mock : Mock):
  logger = Logger()
  logger.debug('debug message')
  assert debug_mock.call_count == 1
  assert debug_mock.call_args[0][0] == 'debug message'
  
@patch('src.service.logger.LOG_FOLDER_PATH', OUTPUT_FOLDER_PATH)
@patch('src.service.logger.logging.error')
def test_debug (error_mock : Mock):
  logger = Logger()
  logger.error('error message')
  assert error_mock.call_count == 1
  assert error_mock.call_args[0][0] == 'error message'

@patch('src.service.logger.LOG_FOLDER_PATH', OUTPUT_FOLDER_PATH)
@patch('src.service.logger.json_dump')
def test_dump_dict (json_dump_mock : Mock):
  d = {'key': 'value'}
  logger = Logger()
  logger.dump_dict(d)
  assert json_dump_mock.call_count == 1
  assert json_dump_mock.call_args[0][0] == d

@patch('src.service.logger.LOG_FOLDER_PATH', OUTPUT_FOLDER_PATH)
def test_clear ():
  prepare_output_folder()
  with open(f'{OUTPUT_FOLDER_PATH}/lyd.log', 'w') as f:
    f.write('log')
  open(f'{OUTPUT_FOLDER_PATH}/test.json', 'w').close()
  
  logger = Logger()
  logger.clear()
  with open(f'{OUTPUT_FOLDER_PATH}/lyd.log', 'r') as f:
    assert f.read() == ''
  assert len(listdir(OUTPUT_FOLDER_PATH)) == 1
