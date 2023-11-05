from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch

from src.section.ListSubtitleSection import ListSubtitleSection, VALUE

@patch('builtins.input', return_value='Y')
@patch('src.section.ListSubtitleSection.YoutubeDL')
def test_list_format(youtubeDl_mock, input_mock):
  ListSubtitleSection('').run('')

  called_paramCommands = youtubeDl_mock.call_args.kwargs['params']
  assert called_paramCommands['listsubtitles'] == True

@patch('src.section.ListSubtitleSection.YoutubeDL')
@patch('builtins.input')
def test_not_list_format(input_mock, youtubeDl_mock):
  section = ListSubtitleSection('')

  input_mock.return_value = VALUE.IN_NOT_LIST.value
  section.run('')

  input_mock.return_value = VALUE.IN_EMPTY.value
  section.run('')

  assert youtubeDl_mock.call_count == 0