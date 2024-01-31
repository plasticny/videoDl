from src.service.urlHelper import *

def test_isValid():
  # youtube
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  valid, _ = isValid(url)
  assert valid == True
  
  url = "https://www.youtube.com/watch"
  valid, _ = isValid(url)
  assert valid == False

  # not a valid url
  url = "not a valid url"
  valid, _ = isValid(url)
  assert valid == False

def test_getSource():
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  source = getSource(url)
  assert source is UrlSource.YOUTUBE
  
  url = "https://youtu.be/dQw4w9WgXcQ"
  source = getSource(url)
  assert source is UrlSource.YOUTU_BE

  url = "https://www.bilibili.com/video/BV1Kb411W75N"
  source = getSource(url)
  assert source is UrlSource.BILIBILI

  url = "https://www.facebook.com/watch/?v=10158340980295851"
  source = getSource(url)
  assert source is UrlSource.FACEBOOK
  
  url = "https://www.instagram.com/p/CP9QqZ0nZ6I/"
  source = getSource(url)
  assert source is UrlSource.IG

  url = "https://example.com"
  source = getSource(url)
  assert source is UrlSource.NOT_DEFINED

def test_removeSurplusParam():
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
  expected_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  result = removeSurplusParam(url)
  assert result == expected_url

  url = "https://www.bilibili.com/video/BV1Kb411W75N?spm_id_from=333.851.b_7265636f6d6d656e64.1"
  expected_url = "https://www.bilibili.com/video/BV1Kb411W75N"
  result = removeSurplusParam(url)
  assert result == expected_url
  
  url = "https://www.facebook.com/watch/?v=10158340980295851&ref=sharing"
  expected_url = "https://www.facebook.com/watch/?v=10158340980295851"
  result = removeSurplusParam(url)
  assert result == expected_url

  url = "https://example.com"
  assert removeSurplusParam(url) == url
