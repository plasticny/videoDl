from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch
from pytest import raises as pytest_raises

from tests.fakers import fake_CommandConverter, fake_runCommand

from src.section.ListSubtitleSection import ListSubtitleSection
from src.dlConfig import dlConfig

@patch('builtins.input', return_value='Y')
@patch('src.section.ListSubtitleSection.CommandConverter')
@patch('src.section.ListSubtitleSection.runCommand', fake_runCommand)
def test_list_format(mock_cc, mock_input):
  section = ListSubtitleSection('', dlConfig())

  # make sure the property listFormat of ComandConverter is called
  mock_cc.return_value = fake_CommandConverter(None, doListSubs=False)
  with pytest_raises(Exception) as excinfo:
    section.run()
  assert excinfo.type == AttributeError

  mock_cc.return_value = fake_CommandConverter(None, doListSubs=True)
  section.run()

@patch('builtins.input')
# when not list format, the part with CommandConverter should not be called
# mock it with an empty one, so a failure will be raised if it is called
@patch('src.section.ListSubtitleSection.CommandConverter')
def test_not_list_format(mock_cc, mock_input):
  mock_cc.return_value = fake_CommandConverter(None, doListSubs=False)

  mock_input.return_value = 'N'
  ListSubtitleSection('', dlConfig()).run()

  mock_input.return_value = ''
  ListSubtitleSection('', dlConfig()).run()