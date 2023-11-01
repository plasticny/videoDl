from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch, call
from pytest import raises as pytest_raises

from tests.fakers import fake_CommandConverter

from src.section.ListFormatSection import ListFormatSection
from src.dlConfig import dlConfig

@patch('builtins.input', return_value='Y')
@patch('src.section.ListFormatSection.CommandConverter')
@patch('src.section.ListFormatSection.runCommand')
def test_list_format(runCommand_mock, mock_cc, mock_input):
  section = ListFormatSection('', dlConfig())

  cc = fake_CommandConverter(None)

  mock_cc.return_value = cc
  section.run()

  called_paramCommands = runCommand_mock.call_args.kwargs['paramCommands']
  assert called_paramCommands.count(cc.listFormat) == 1
  assert called_paramCommands.count(cc.cookies) == 1

@patch('builtins.input')
# when not list format, the part with CommandConverter should not be called
# mock it with an empty one, so a failure will be raised if it is called
@patch('src.section.ListFormatSection.CommandConverter')
def test_not_list_format(mock_cc, mock_input):
  mock_cc.return_value = fake_CommandConverter(None)

  mock_input.return_value = 'N'
  ListFormatSection('', dlConfig()).run()

  mock_input.return_value = ''
  ListFormatSection('', dlConfig()).run()