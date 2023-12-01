from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch
from pytest import raises as pytest_raises
from os import listdir
from os.path import exists

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.section.DownloadSection import DownloadSection
from src.service.YtDlpHelper import Opts
from src.service.structs import Subtitle

@patch('src.section.DownloadSection.YoutubeDL.download')
def test_with_fail_download(download_mock):
  download_mock.side_effect = Exception()

  with pytest_raises(Exception):
    DownloadSection().run('url', Opts(), retry=2)  

  # check if download is called 3 times
  assert download_mock.call_count == 3

@patch('src.section.DownloadSection.YoutubeDL.download_with_info_file')
@patch('src.section.DownloadSection.YoutubeDL.download')
def test_use_info_file(download_mock, download_w_file_mock):
  """Test if info file is used when info_path is not None"""
  # test info_path is not None
  DownloadSection().run('url', Opts(), info_path='info_path')
  assert download_w_file_mock.call_count == 1
  assert download_mock.call_count == 0

  # test info_path is None
  download_mock.reset_mock()
  download_w_file_mock.reset_mock()
  DownloadSection().run('url', Opts(), info_path=None)
  assert download_w_file_mock.call_count == 0
  assert download_mock.call_count == 1

def test_with_real_download_yt():
  prepare_output_folder()

  opts = Opts()
  opts.outputDir = OUTPUT_FOLDER_PATH
  opts.outputName = 'test.mp4'
  opts.format = '269'
  opts.setSubtitle(Subtitle('en', 'en', False))
  DownloadSection().run(
    url='https://www.youtube.com/watch?v=JMu9kdGHU3A',
    opts=opts
  )

  fileNms = listdir(OUTPUT_FOLDER_PATH)
  assert len(fileNms) == 2
  assert 'test.mp4' in fileNms
  assert 'test.en.vtt' in fileNms

def test_with_real_download_bili():
  prepare_output_folder()

  opts = Opts()
  opts.outputDir = OUTPUT_FOLDER_PATH
  DownloadSection().run(
    url='https://www.bilibili.com/video/BV1154y1T765',
    opts=opts
  )

  assert exists(f'{OUTPUT_FOLDER_PATH}/小 僧 觉 得 很 痛 [BV1154y1T765].mp4')

@patch('src.section.DownloadSection.YoutubeDL.download')
def test_not_change_param_opts(_):
  opts = Opts()
  backup_opts = opts.copy()
  DownloadSection().run('url', opts)
  assert opts == backup_opts