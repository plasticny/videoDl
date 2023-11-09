from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch

from src.section.FormatSection import FormatSection, VALUE
from src.service.YtDlpHelper import Opts

@patch('builtins.input')
def test_with_auto_format(input_mock):
  section = FormatSection('')

  input_mock.return_value = VALUE.IN_AUTO.value
  opts = section.run()
  assert opts()["format"] == VALUE.OUT_DEFAULT.value

  input_mock.return_value = VALUE.IN_EMPTY.value
  opts = section.run()
  assert opts()["format"] == VALUE.OUT_DEFAULT.value

@patch('builtins.input')
def test_with_format(input_mock):
  section = FormatSection('')

  input_mock.return_value = 'mp4'
  opts = section.run()
  assert opts()["format"] == 'mp4'

  input_mock.return_value = 'mkv'
  opts = section.run()
  assert opts()["format"] == 'mkv'

  input_mock.return_value = '123'
  opts = section.run()
  assert opts()["format"] == '123'

@patch('builtins.input', return_value='mp4')
def test_not_change_param_opts(_):
  opts = Opts()
  backup_opts = opts.copy()
  FormatSection('').run(opts)
  assert opts == backup_opts