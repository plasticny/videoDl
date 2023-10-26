from sys import path as sys_path
sys_path.append('src')

from unittest.mock import patch, ANY
from pytest import raises as pytest_raises

from src.service.YtFetcher import *

def test_getYtSongTitle():
  title = getYtSongTitle('https://www.youtube.com/watch?v=skPMeWaUfB0')
  assert title == 'ONE OFF MIND'

def test_getYtSongTitle_not_url():
  with pytest_raises(ValueError) as e:
    getYtSongTitle('not url')
  assert e.type == ValueError
  assert str(e.value) == ErrMessage.INVALID_URL.value

def test_getYtSongTitle_not_yt_url():
  with pytest_raises(ValueError) as e:
    getYtSongTitle('https://www.bilibili.com/video/BV1Kb411W75N')
  assert e.type == ValueError
  assert str(e.value) == ErrMessage.NOT_YT_URL.value

def test_escapeSpecialChar():
  title = ''.join(list(ESCAPE_CHR)) + 'test'
  escaped = escapeSpecialChar(title)

  assert escaped == '_' * len(ESCAPE_CHR) + 'test'

# test getYtSongTitle with escape=True
@patch('src.service.YtFetcher.escapeSpecialChar')
def test_getYtSongTitle_escape(esc_mock):
  esc_mock.return_value = 'escaped'
  title = getYtSongTitle('https://www.youtube.com/watch?v=skPMeWaUfB0', escape=True)
  assert title == 'escaped'
  esc_mock.assert_called_once_with(ANY)
