from sys import path
path.append('src')

from unittest.mock import patch
from os.path import exists

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.dl import Dl
from src.service.YtDlpHelper import Opts
from src.service.MetaData import VideoMetaData, PlaylistMetaData

@patch('src.dl.Dl.download')
@patch('src.dl.Dl.setup')
@patch('src.dl.fetchMetaData')
@patch('src.dl.Dl.login')
@patch('src.dl.UrlSection.run')
def test_download_call_count(
    url_mock, login_mock, fetch_mock, setup_mock, download_mock
  ):
  class fake_videoMd(VideoMetaData):
    @property
    def title(self):
      return None
    @property
    def url(self):
      return None
    def __init__(self, *args, **kwargs):
      pass
  class fake_playlistMd(PlaylistMetaData):
    @property
    def title(self):
      return None
    @property
    def url(self):
      return None
    @property
    def videos(self):
      return [fake_videoMd() for _ in range(3)]
    def __init__(self, *args, **kwargs):
      pass
  def fake_login(url, opts):
    return opts
  def fake_setup(md, opts_ls):
    return opts_ls

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  login_mock.side_effect = fake_login
  # fetch will be mocked in each test
  setup_mock.side_effect = fake_setup

  # test video
  fetch_mock.return_value = fake_videoMd()
  Dl().run(loop=False)
  assert download_mock.call_count == 1

  # test playlist
  download_mock.reset_mock()
  fetch_mock.return_value = fake_playlistMd()
  Dl().run(loop=False)
  assert download_mock.call_count == 3

@patch('src.dl.Dl.setup')
@patch('src.dl.ListFormatSection.run')
@patch('src.dl.LoginSection.run')
@patch('src.dl.UrlSection.run')
def test_run(url_mock, login_mock, _, setup_mock):
  def fake_login(opts):
    return opts
  def fake_setup(md, opts_ls:list[Opts]):
    res = []
    for opts in opts_ls:
      o = opts.copy()
      o.outputDir = OUTPUT_FOLDER_PATH
      res.append(o)
    return res

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  login_mock.side_effect = fake_login
  setup_mock.side_effect = fake_setup

  prepare_output_folder()
  Dl().run(loop=False)

  assert exists(f'{OUTPUT_FOLDER_PATH}/test video for ＂videoDl＂ [JMu9kdGHU3A].mkv')