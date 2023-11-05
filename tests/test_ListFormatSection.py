from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch

from src.section.ListFormatSection import ListFormatSection, VALUE

@patch('builtins.input', return_value='Y')
@patch('src.section.ListFormatSection.YoutubeDL')
def test_list_format(youtubeDl_mock, input_mock):
  ListFormatSection('').run('')

  called_paramCommands = youtubeDl_mock.call_args.kwargs['params']
  assert called_paramCommands['listformats'] == True

@patch('src.section.ListFormatSection.YoutubeDL')
@patch('builtins.input')
def test_not_list_format(input_mock, youtubeDl_mock):
  section = ListFormatSection('')

  input_mock.return_value = VALUE.IN_NOT_LIST.value
  section.run('')

  input_mock.return_value = VALUE.IN_EMPTY.value
  section.run('')

  assert youtubeDl_mock.call_count == 0