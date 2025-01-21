from dataclasses import dataclass
from uuid import uuid4

from src.structs.option import Opt

class fake_opt (Opt):
  def __init__(self) -> None:
    pass

def test_init ():
  @dataclass
  class Case ():
    # args
    other : Opt
    # expected
    expected_url : str
    expected_cookie_file_path : str
    expected_login_browser : str

  other = Opt()
  other.url = str(uuid4())
  other.cookie_file_path = str(uuid4())
  other.login_browser = str(uuid4())

  cases: list[Case] = [
    # no other passed
    Case(
      other = None,
      expected_url = None,
      expected_cookie_file_path = None,
      expected_login_browser = None
    ),
    # other passed
    Case(
      other = other,
      expected_url = other.url,
      expected_cookie_file_path = other.cookie_file_path,
      expected_login_browser = other.login_browser
    )
  ]

  for idx, case in enumerate(cases):
    print(f'test_init - case {idx}')
    opt = Opt(case.other)
    assert opt.url == case.expected_url
    assert opt.cookie_file_path == case.expected_cookie_file_path
    assert opt.login_browser == case.expected_login_browser

def test_to_ytdlp_opt():
  url = 'https://www.youtube.com/watch?v=123'
  cookie_file_path = 'cookie.txt'
  browser = 'firefox'
  
  opt = fake_opt()
  opt.url = url
  opt.cookie_file_path = cookie_file_path
  opt.login_browser = browser
  assert Opt.to_ytdlp_opt(opt) == {
    'cookiefile': 'cookie.txt',
    'login_browser': 'firefox'
  }
