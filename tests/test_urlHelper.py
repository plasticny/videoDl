from pytest import raises as pytest_raises

from src.service.urlHelper import *

# =========== isValid =========== #
def test_isValid_valid_youtube_url():
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  valid, err = isValid(url)
  assert valid == True
  assert err == None

def test_isValid_invalid_youtube_url():
  url = "https://www.youtube.com/watch"
  valid, err = isValid(url)
  assert valid == False
  assert err == ErrMessage.INVALID_YOUTUBE_URL.value

def test_isValid_invalid_url():
  url = "not a valid url"
  valid, err = isValid(url)
  assert valid == False
  assert err == ErrMessage.INVALID_URL.value
# =========== End isValid =========== #

# ========== getSource ========== #
def test_getSource_youtube():
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  source = getSource(url)
  assert source == UrlSource.YOUTUBE

def test_getSource_youtube_short():
  url = "https://youtu.be/dQw4w9WgXcQ"
  source = getSource(url)
  assert source == UrlSource.YOUTUBE

def test_getSource_bilibili():
  url = "https://www.bilibili.com/video/BV1Kb411W75N"
  source = getSource(url)
  assert source == UrlSource.BILIBILI

def test_getSource_not_defined():
  url = "https://example.com"
  source = getSource(url)
  assert source == UrlSource.NOT_DEFINED
# ========== End getSource ========== #

# ========== removeSurplusParam ========== #
def test_removeSurplusParam_youtube():
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
  expected_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  result = removeSurplusParam(url)
  assert result == expected_url

def test_removeSurplusParam_bilibili():
  url = "https://www.bilibili.com/video/BV1Kb411W75N?spm_id_from=333.851.b_7265636f6d6d656e64.1"
  expected_url = "https://www.bilibili.com/video/BV1Kb411W75N"
  result = removeSurplusParam(url)
  assert result == expected_url

def test_removeSurplusParam_not_defined():
  url = "https://example.com"
  with pytest_raises(NotImplementedError) as e_info:
    removeSurplusParam(url)
  assert e_info.type == NotImplementedError
# ========== End removeSurplusParam ========== #
