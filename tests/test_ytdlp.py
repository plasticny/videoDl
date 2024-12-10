from unittest.mock import patch, Mock
from uuid import uuid4

from src.service.ytdlp import Ytdlp, YT_DLP_PATH as EXE_NM

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
  assert len(cmd_comp) == 5
  assert base_cmd in cmd_comp
  assert '-J' in cmd_comp
  assert '--list-subs' in cmd_comp
  assert '-q' in cmd_comp
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
