from src.structs.option import IOpt

class fake_opt (IOpt):
  def __init__(self) -> None:
    pass

def test_to_ytdlp_opt():
  url = 'https://www.youtube.com/watch?v=123'
  cookie_file_path = 'cookie.txt'
  
  opt = fake_opt()
  opt.url = url
  opt.cookie_file_path = cookie_file_path
  assert IOpt.to_ytdlp_opt(opt) == {
    'cookiefile': 'cookie.txt'
  }
