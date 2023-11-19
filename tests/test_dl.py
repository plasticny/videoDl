from sys import path
path.append('src')

from unittest.mock import patch
from os.path import exists

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.dl import Dl
from src.service.YtDlpHelper import Opts

@patch('src.dl.Dl.setup')
@patch('src.dl.ListFormatSection.run')
@patch('src.dl.LoginSection.run')
@patch('src.dl.UrlSection.run')
def test_run(url_mock, login_mock, _, setup_mock):
  def fake_login(opts):
    return opts
  def fake_setup(md, opts:Opts):
    opts = opts.copy()
    opts.outputDir = OUTPUT_FOLDER_PATH
    return opts

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  login_mock.side_effect = fake_login
  setup_mock.side_effect = fake_setup

  prepare_output_folder()
  Dl().run(loop=False)

  assert exists(f'{OUTPUT_FOLDER_PATH}/test video for ＂videoDl＂ [JMu9kdGHU3A].mkv')