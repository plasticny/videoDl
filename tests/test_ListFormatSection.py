from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from src.section.ListFormatSection import ListFormatSection

class fake_opt ():
  @property
  def url (self):
    return 'url'
  def copy (self):
    return self

@patch('builtins.input', return_value='Y')
@patch('src.section.ListFormatSection.YoutubeDL')
def test_list_format(youtubeDl_mock:Mock, input_mock):
  ListFormatSection('').run(fake_opt())

  called_paramCommands = youtubeDl_mock.call_args.args[0]
  assert called_paramCommands['listformats'] == True

@patch('src.section.ListFormatSection.YoutubeDL')
@patch('builtins.input')
def test_not_list_format(input_mock, youtubeDl_mock):
  section = ListFormatSection('')

  input_mock.return_value = 'N'
  section.run(fake_opt())

  input_mock.return_value = ''
  section.run(fake_opt())

  assert youtubeDl_mock.call_count == 0