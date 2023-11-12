from sys import path
path.append('src')

from unittest.mock import patch
from pytest import raises as pytest_raises

from uuid import uuid4
from os.path import exists
from pymediainfo import MediaInfo

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

def test_renameFile_escape():
  """
    test renameFile function escape special char and rename file correctly
  """
  prepare_output_folder()

  # create a test file
  old_title = f'{str(uuid4())}.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{old_title}', 'w'):
    pass

  new_title = '"*:<>?|test.txt'
  expected_escape_title = 'test.txt'
  lazyYtDownload().renameFile(
    oldName=old_title, newName=new_title,
    dirPath=OUTPUT_FOLDER_PATH
  )

  assert not exists(f'{OUTPUT_FOLDER_PATH}\\{old_title}')
  assert exists(f'{OUTPUT_FOLDER_PATH}\\{expected_escape_title}')

def test_renameFile_overwrite():
  """
    test renameFile can overwrite file, if overwrite is true and file is exist
  """
  prepare_output_folder()

  # create a old file that will be rename
  old_title = 'old.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{old_title}', 'w') as f:
    f.write('old')
  
  # create a existed file that will be overwrite
  new_title = 'new.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{new_title}', 'w') as f:
    f.write('new')

  # expect a error will be raise if not overwrite
  with pytest_raises(FileExistsError):
    lazyYtDownload().renameFile(
      oldName=old_title, newName=new_title,
      dirPath=OUTPUT_FOLDER_PATH,
      overwrite=False
    )

  # rename and overwrite
  lazyYtDownload().renameFile(
    oldName=old_title, newName=new_title,
    dirPath=OUTPUT_FOLDER_PATH,
    overwrite=True
  )

  # check file content
  assert not exists(f'{OUTPUT_FOLDER_PATH}\\{old_title}')
  assert exists(f'{OUTPUT_FOLDER_PATH}\\{new_title}')
  with open(f'{OUTPUT_FOLDER_PATH}\\{new_title}', 'r') as f:
    assert f.read() == 'old'

@patch('src.lazyYtDownload.lazyYtDownload.configDownload')
@patch('builtins.input')
def test_download_yt_video(input_mock, config_mock):
  prepare_output_folder()

  input_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'

  opts = Opts()
  opts.outputDir = OUTPUT_FOLDER_PATH
  opts.writeSubtitles = True
  opts.subtitlesLang = 'en'
  opts.embedSubtitle = True
  config_mock.return_value = opts

  lazyYtDownload().run(loop=False)

  outputFile_path = f'{OUTPUT_FOLDER_PATH}/test video for videoDl.mp4'

  assert exists(outputFile_path)

  found_subtitle_track = False
  for track in MediaInfo.parse(outputFile_path).tracks:
    if track.track_type == 'Text':
      found_subtitle_track = True
      break
  assert found_subtitle_track

@patch('src.lazyYtDownload.OutputSection.run')
@patch('builtins.input')
def test_download_bili_video(input_mock, outputSection_mock):
  prepare_output_folder()

  input_mock.side_effect = [
    'https://www.bilibili.com/video/BV1154y1T765', # url
    'N', # login
    'Y', # list subtitle
    'N' # write subtitle
  ]

  def outputSection_faker(self, opts:Opts, askDir:bool=True, askName:bool=True) -> Opts:
    opts = opts.copy()
    opts.outputDir = OUTPUT_FOLDER_PATH
    return opts

  with patch('src.lazyYtDownload.OutputSection.run', outputSection_faker):
    lazyYtDownload().run(loop=False)
  assert exists(f'{OUTPUT_FOLDER_PATH}/小 僧 觉 得 很 痛.mp4')