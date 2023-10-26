from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch
from pytest import raises as pytest_raises

from tests.fakers import fake_CommandConverter, fake_runCommand

from src.section.ListFormatSection import ListFormatSection
from src.dlConfig import dlConfig

@patch('builtins.input', return_value='Y')
@patch('src.section.ListFormatSection.CommandConverter')
@patch('src.section.ListFormatSection.runCommand', fake_runCommand)
def test_list_format(mock_cc, mock_input):
  section = ListFormatSection('', dlConfig())

  # make sure the property listFormat of ComandConverter is called
  mock_cc.return_value = fake_CommandConverter(None, doListFormat=False)
  with pytest_raises(Exception) as excinfo:
    section.run()
  assert excinfo.type == AttributeError

  mock_cc.return_value = fake_CommandConverter(None, doListFormat=True)
  section.run()

@patch('builtins.input')
# when not list format, the part with CommandConverter should not be called
# mock it with an empty one, so a failure will be raised if it is called
@patch('src.section.ListFormatSection.CommandConverter')
def test_not_list_format(mock_cc, mock_input):
  mock_cc.return_value = fake_CommandConverter(None, doListFormat=False)

  mock_input.return_value = 'N'
  ListFormatSection('', dlConfig()).run()

  mock_input.return_value = ''
  ListFormatSection('', dlConfig()).run()