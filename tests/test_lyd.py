from sys import path
path.append('src')

from unittest.mock import patch, Mock

from uuid import uuid4
from os.path import exists

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.lazyYtDownload import lazyYtDownload
from src.service.YtDlpHelper import Opts

# test login function
@patch('src.lazyYtDownload.LoginSection.run')
def test_login(login_mock):
  lyd = lazyYtDownload()

  # test other
  lyd.login('other', Opts())
  login_mock.assert_not_called()

  # test bilibili
  lyd.login('www.bilibili.com/video/BV1QK4y1d7dQ', Opts())
  login_mock.assert_called_once()

@patch('src.lazyYtDownload.lazyYtDownload.download')
@patch('src.lazyYtDownload.lazyYtDownload.configDownload')
@patch('src.lazyYtDownload.UrlSection.run')
def test_download_call_count_yt_video(url_mock, _, download_mock):
  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  lazyYtDownload().run(loop=False)
  assert download_mock.call_count == 1

@patch('src.lazyYtDownload.lazyYtDownload.download')
@patch('src.lazyYtDownload.lazyYtDownload.configDownload')
@patch('src.lazyYtDownload.UrlSection.run')
def test_download_call_count_bili_list(url_mock, _, download_mock):
  url_mock.return_value = 'https://www.bilibili.com/video/BV1bN411s7VT'
  lazyYtDownload().run(loop=False)
  assert download_mock.call_count == 3

@patch('src.lazyYtDownload.lazyYtDownload.configDownload')
@patch('builtins.input')
def test_download_yt_video(input_mock, config_mock):
  prepare_output_folder()

  input_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  config_mock.return_value = Opts().outputDir(OUTPUT_FOLDER_PATH)

  lazyYtDownload().run(loop=False)
  assert exists(f'{OUTPUT_FOLDER_PATH}/test video for videoDl.mp4')


@patch('src.lazyYtDownload.OutputSection.run')
@patch('builtins.input')
def test_download_fullRun_bili_video(input_mock, outputSection_mock):
  prepare_output_folder()

  input_mock.side_effect = [
    'https://www.bilibili.com/video/BV1154y1T765', # url
    'N', # login
    'Y', # list subtitle
    'Y', # write subtitle
    '', # subtitle lang
    'N', # write auto subtitle
  ]

  def outputSection_faker(self, opts:Opts, askDir:bool=True, askName:bool=True) -> Opts:
    return opts.copy().outputDir(OUTPUT_FOLDER_PATH)

  with patch('src.lazyYtDownload.OutputSection.run', outputSection_faker):
    lazyYtDownload().run(loop=False)
  assert exists(f'{OUTPUT_FOLDER_PATH}/小 僧 觉 得 很 痛.mp4')

# test renameFile function escape special char and rename file correctly
def test_renameFile():
  # create a test file
  old_title = f'{str(uuid4())}.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{old_title}', 'w'):
    pass

  new_title = '"*:<>?|test.txt'
  expected_escape_title = 'test.txt'
  lazyYtDownload().renameFile(OUTPUT_FOLDER_PATH, old_title, new_title)

  assert not exists(f'{OUTPUT_FOLDER_PATH}\\{old_title}')
  assert exists(f'{OUTPUT_FOLDER_PATH}\\{expected_escape_title}')