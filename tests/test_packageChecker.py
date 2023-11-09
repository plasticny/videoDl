from unittest.mock import patch, mock_open
from pytest import raises as pytest_raises

from src.service.packageChecker import versionToInt, check

def test_versionToInt():
  assert versionToInt(' 2021.10.13 ') == 8117
  assert versionToInt('2021.10.13.1') == 16235

@patch('src.service.packageChecker.pip.main')
@patch('src.service.packageChecker.version')
def test_check(version_mock, pip_mock):
  with open('tests\\testFiles\\test_packageChecker\\requirement.txt', 'r') as f:
    read_data = f.read()

  version_mock.side_effect = [
    "0.1.0",    # fullfill
    "0.1.0",    # not fullfill (need upgrade)
    Exception() # cannot get version (need install)
  ]

  with patch('builtins.open', mock_open(read_data=read_data)):
    check()

  assert pip_mock.call_count == 2