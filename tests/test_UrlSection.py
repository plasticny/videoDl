from sys import path as sys_path
sys_path.append('src')

from unittest.mock import patch, Mock

from src.section.UrlSection import UrlSection, Message
from src.service.urlHelper import ErrMessage

def test(capfd):
  section = UrlSection('Url')

  # input mocks
  input_mock_empty_url = Mock()
  input_mock_empty_url.strip.return_value = ''

  input_mock_invalid_url = Mock()
  input_mock_invalid_url.strip.return_value = 'invalid url'

  input_mock_valid_url = Mock()
  input_mock_valid_url.strip.return_value = 'https://www.youtube.com/watch?v=123&list=123'

  input_mock = Mock()
  input_mock.side_effect = [input_mock_empty_url, input_mock_invalid_url, input_mock_valid_url]

  # execute
  with patch('builtins.input', input_mock):
    url = section.run()

    out, err = capfd.readouterr()

    expected_out = f'{section.header}\n'
    expected_out += f'{Message.EMPTY_URL.value}\n'
    expected_out += f'{ErrMessage.INVALID_URL.value}\n'
    expected_out += f'{section.footer}\n'
    assert out == expected_out
    assert err == ''

    assert url == 'https://www.youtube.com/watch?v=123'