from unittest.mock import patch, Mock
from uuid import uuid4
from dataclasses import dataclass
from typing import Optional
from pytest import raises as pytest_raises

from src.service.ytdlp import Ytdlp, YT_DLP_PATH as EXE_NM, YT_DLP_URL

def test_build_base_cmd ():
  # empty opt
  ytdlp = Ytdlp()
  cmd_comp = ytdlp.base_cmd.split(' ')
  assert len(cmd_comp) == 4
  assert EXE_NM in cmd_comp
  
  # with opt, but all negative value
  ytdlp = Ytdlp({
    'cookiefile': None,
    'login_browser': None,
    'extract_flat': False,
    'format': None,
    'overwrites': False,
    'quiet': False,
    'skip_download': False,
    'writesubtitles': False,
    'writeautomaticsub': False,
    'subtitleslangs': None,
    'paths': None,
    'outtmpl': None
  })
  cmd_comp = ytdlp.base_cmd.split(' ')
  assert len(cmd_comp) == 4
  assert EXE_NM in cmd_comp
  
  # with opt
  opt = {
    'cookiefile': str(uuid4()),
    'login_browser': str(uuid4()),
    'extract_flat': True,
    'format': str(uuid4()),
    'overwrites': True,
    'quiet': True,
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': [str(uuid4()), str(uuid4())],
    'paths': {'home': str(uuid4())},
    'outtmpl': str(uuid4())
  }
  ytdlp = Ytdlp(opt)
  assert EXE_NM in ytdlp.base_cmd
  assert f'--cookies {opt["cookiefile"]}' in ytdlp.base_cmd
  assert f'--cookies-from-browser {opt["login_browser"]}' in ytdlp.base_cmd
  assert '--flat-playlist' in ytdlp.base_cmd
  assert f'--format {opt["format"]}' in ytdlp.base_cmd
  assert '--force-overwrite' in ytdlp.base_cmd
  assert '-q' in ytdlp.base_cmd
  assert '--skip-download' in ytdlp.base_cmd
  assert '--write-sub' in ytdlp.base_cmd
  assert '--write-auto-sub' in ytdlp.base_cmd
  assert f'--sub-lang {",".join(opt["subtitleslangs"])}' in ytdlp.base_cmd
  assert f'-P {opt["paths"]["home"]}' in ytdlp.base_cmd
  assert f'-o {opt["outtmpl"]}' in ytdlp.base_cmd

@patch('src.service.ytdlp.loads')
@patch('src.service.ytdlp.popen')
@patch('src.service.ytdlp.Ytdlp._build_base_cmd')
def test_extract_info (base_cmd_mock: Mock, popen_mock: Mock, loads_mock: Mock):
  class fakePopenRet:
    def read (self) -> str:
      return '\n\n'
  
  base_cmd = str(uuid4())
  url = str(uuid4())
  
  base_cmd_mock.return_value = base_cmd
  popen_mock.side_effect = lambda _: fakePopenRet()
  loads_mock.return_value = {}
  
  Ytdlp().extract_info(url)
  
  popen_mock.assert_called_once()
  
  cmd: str = popen_mock.call_args[0][0]
  cmd_comp = cmd.split(' ')
  assert len(cmd_comp) == 4
  assert base_cmd in cmd_comp
  assert '-J' in cmd_comp
  assert '--list-subs' in cmd_comp
  assert url in cmd_comp

@patch('src.service.ytdlp.run_cmd')
@patch('src.service.ytdlp.Ytdlp._build_base_cmd')
def test_download (base_cmd_mock: Mock, run_cmd_mock: Mock):
  base_cmd = str(uuid4())
  url = str(uuid4())
  
  base_cmd_mock.return_value = base_cmd  

  Ytdlp().download(url)
  
  run_cmd_mock.assert_called_once()
  
  cmd: str = run_cmd_mock.call_args[0][0]
  cmd_comp = cmd.split(' ')
  assert len(cmd_comp) == 2
  assert base_cmd in cmd_comp
  assert url in cmd_comp

@patch('builtins.open')
@patch('src.service.ytdlp.get')
@patch('src.service.ytdlp.exists')
def test_ensure_installed (
  exists_mock: Mock,
  get_request_mock: Mock,
  open_mock: Mock
):
  class fakeResponse:
    def __init__(self, status_code: int):
      self.status_code = status_code
      self.content = str(uuid4())

  def fake_open (path: str, mode: str):
    class fakeBufferedWriter:
      def __enter__ (self):
        return self
      
      def __exit__ (self, *args):
        pass

      def write (self, content: str):
        pass
    return fakeBufferedWriter()

  @dataclass
  class Case:
    exists_ret: bool
    get_request_ret: Optional[fakeResponse]
    error_raised: bool

  case_ls: list[Case] = [
    # already installed
    Case(True, None, False),
    Case(False, fakeResponse(200), False),
    Case(False, fakeResponse(404), True)
  ]

  for case in case_ls:
    exists_mock.reset_mock()
    get_request_mock.reset_mock()
    open_mock.reset_mock()

    exists_mock.return_value = case.exists_ret
    get_request_mock.return_value = case.get_request_ret
    open_mock.side_effect = fake_open

    if case.error_raised:
      with pytest_raises(Exception):
        Ytdlp().ensure_installed()
    else:    
      Ytdlp().ensure_installed()

    if not case.exists_ret:
      get_request_mock.assert_called_once()
      get_request_mock.call_args[0][0] == YT_DLP_URL

      if not case.error_raised:
        open_mock.assert_called_once_with(EXE_NM, 'wb')
