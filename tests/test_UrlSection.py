from unittest.mock import patch, call, Mock

from src.section.UrlSection import UrlSection, Message
from src.service.urlHelper import ErrMessage

@patch('builtins.print')
@patch('builtins.input')
def test_problematic_url(input_mock : Mock, print_mock : Mock):
  section = UrlSection(doShowHeader=False, doShowFooter=False)

  # test problematic url
  input_mock.side_effect = [
    '', # empty url
    'invalid url', # invalid url
    'https://www.nicovideo.jp/watch/sm32010061' # unhandled url source
  ]

  url = section.run()
  assert print_mock.mock_calls[0] == call(Message.EMPTY_URL.value)
  assert print_mock.mock_calls[1] == call(ErrMessage.INVALID_URL.value)
  assert print_mock.mock_calls[2] == call(Message.URL_SOURCE_NOT_TESTED.value)
  assert url == 'https://www.nicovideo.jp/watch/sm32010061'

# test url that should be well handled
@patch('builtins.print')
@patch('builtins.input')
def test_valid_url(input_mock : Mock, print_mock : Mock):
  input_mock.return_value = 'https://www.youtube.com/watch?v=9bZkp7q19f0'
  assert UrlSection(doShowHeader=False, doShowFooter=False).run() == 'https://www.youtube.com/watch?v=9bZkp7q19f0'
  assert print_mock.mock_calls == []
