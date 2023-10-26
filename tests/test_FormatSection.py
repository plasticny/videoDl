from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch, call

from src.section.FormatSection import FormatSection, Message, VALUE

@patch('builtins.input')
def test_with_auto_format(input_mock):
  section = FormatSection('')

  input_mock.return_value = VALUE.IN_AUTO.value
  result = section.run()
  assert result == VALUE.OUT_DEFAULT.value

  input_mock.return_value = VALUE.IN_EMPTY.value
  result = section.run()
  assert result == VALUE.OUT_DEFAULT.value

@patch('builtins.input')
def test_with_format(input_mock):
  section = FormatSection('')

  input_mock.return_value = 'mp4'
  result = section.run()
  assert result == 'mp4'

  input_mock.return_value = 'mkv'
  result = section.run()
  assert result == 'mkv'

  input_mock.return_value = '123'
  result = section.run()
  assert result == '123'

@patch('builtins.input')
@patch('builtins.print')
def test_ui_output(print_mock, input_mock):
  section = FormatSection('format')
  section.run()

  print_mock.mock_calls[0] == call(section.header)
  input_mock.mock_calls[0] == call(Message.ASK_FORMAT.value)
  print_mock.mock_calls[1] == call(section.footer)