from unittest.mock import patch, Mock

from src.service.urlHelper import *

def test_isValid():
  # test cases [(url, expected_result)]
  case_ls : list[tuple[str, bool]] = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
    ("https://youtube.com/watch?v=dQw4w9WgXcQ", True),
    ("https://youtu.be/dQw4w9WgXcQ", True),
    ("https://www.youtube.com/playlist?list=PLD7UlE9Qf9UZMMwF6XLyWRUJF8koJ3igJ", True),
    ("https://www.youtube.com/shorts/rzV4tZWhqW4", True),
    ("https://youtube.com/playlist?list=PLD7UlE9Qf9UZMMwF6XLyWRUJF8koJ3igJ", True),
    ("https://www.bilibili.com/video/BV1Kb411W75N", True),
    ("https://www.facebook.com/watch/?v=10158340980295851", True),
    ("https://www.instagram.com/p/CP9QqZ0nZ6I/", True),
    ("https://www.pinterest.com/pin/123456789012345678/", True),
    ("https://pin.it/5hI35yyC9", True),
    ("https://x.com/hanae0626/status/1851961991243686380", True),
    ("https://example.com", False),
    ("not a valid url", False)
  ]
  
  for case in case_ls:
    print('testing', case)
    case_url, expected_result = case
    valid, err = isValid(case_url)
    print(err)
    assert valid == expected_result

def test_getSource():
  # test cases [(url, expected_source)]
  case_ls : list[tuple[str, UrlSource]] = [
    ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', UrlSource.YOUTUBE),
    ('https://youtube.com/watch?v=dQw4w9WgXcQ', UrlSource.YOUTUBE),
    ('https://youtu.be/dQw4w9WgXcQ', UrlSource.YOUTU_BE),
    ('https://www.youtube.com/playlist?list=PLD7UlE9Qf9UZMMwF6XLyWRUJF8koJ3igJ', UrlSource.YOUTUBE_LS),
    ('https://www.youtube.com/shorts/rzV4tZWhqW4', UrlSource.YOUTUBE_SHORT),
    ('https://youtube.com/playlist?list=PLD7UlE9Qf9UZMMwF6XLyWRUJF8koJ3igJ', UrlSource.YOUTUBE_LS),
    ('https://www.bilibili.com/video/BV1Kb411W75N', UrlSource.BILIBILI),
    ('https://www.facebook.com/watch/?v=10158340980295851', UrlSource.FACEBOOK),
    ('https://www.instagram.com/p/CP9QqZ0nZ6I/', UrlSource.IG),
    ('https://www.pinterest.com/pin/123456789012345678/', UrlSource.PINTEREST),
    ('https://pin.it/5hI35yyC9', UrlSource.PIN_IT),
    ('https://x.com/hanae0626/status/1851961991243686380', UrlSource.X),
    ('https://example.com', UrlSource.NOT_DEFINED)
  ]
  
  for case in case_ls:
    print('testing', case)
    case_url, expected_source = case
    assert getSource(case_url) == expected_source

def test_removeSurplusParam():
  # test cases [(url, expected_url)]
  case_ls : list[tuple[str, str]] = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ("https://youtu.be/js1CtxSY38I?list=PLot67IosVFw1aOiraoa5zxbM9Y3xjb1EF", "https://youtu.be/js1CtxSY38I"),
    ("https://www.youtube.com/playlist?list=PLD7UlE9Qf9UZMMwF6XLyWRUJF8koJ3igJ", "https://www.youtube.com/playlist?list=PLD7UlE9Qf9UZMMwF6XLyWRUJF8koJ3igJ"),
    ("https://www.bilibili.com/video/BV1Kb411W75N?spm_id_from=333.851.b_7265636f6d6d656e64.1", "https://www.bilibili.com/video/BV1Kb411W75N"),
    ("https://www.facebook.com/watch/?v=10158340980295851&ref=sharing", "https://www.facebook.com/watch/?v=10158340980295851"),
    ("https://www.pinterest.com/pin/123456789012345678/?utm_source=share", "https://www.pinterest.com/pin/123456789012345678/"),
    ("https://example.com", "https://example.com")
  ]
  
  for case in case_ls:
    print('testing', case)
    case_url, expected_url = case
    assert removeSurplusParam(case_url) == expected_url

def test_redirect ():
  case_ls : list[tuple[str, str]] = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "https://youtu.be/dQw4w9WgXcQ"),
    ("https://www.bilibili.com/video/BV1Kb411W75N", "https://www.bilibili.com/video/BV1Kb411W75N"),
    ("https://www.facebook.com/watch/?v=10158340980295851", "https://www.facebook.com/watch/?v=10158340980295851"),
    ("https://www.instagram.com/p/CP9QqZ0nZ6I/", "https://www.instagram.com/p/CP9QqZ0nZ6I/"),
    ("https://www.pinterest.com/pin/123456789012345678/", "https://www.pinterest.com/pin/123456789012345678/"),
    ("https://x.com/hanae0626/status/1851961991243686380", "https://x.com/hanae0626/status/1851961991243686380"),
    ("https://pin.it/5hI35yyC9", "https://www.pinterest.com/pin/979532987693940546")
  ]
  
  for case in case_ls:
    print('testing', case)
    case_url, expected_url = case
    assert redirect(case_url) == expected_url
  