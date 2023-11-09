from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch
from pytest import raises as pytest_raises
from os.path import exists
from pymediainfo import MediaInfo

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.section.DownloadSection import DownloadSection
from src.service.YtDlpHelper import Opts

@patch('src.section.DownloadSection.YoutubeDL.download')
def test_with_fail_download(download_mock):
  download_mock.side_effect = Exception()

  with pytest_raises(Exception):
    DownloadSection().run('url', Opts(), retry=2)  

  # check if runCommand is called 3 times
  assert download_mock.call_count == 3

def test_with_real_download_yt():
  prepare_output_folder()

  opts = Opts()
  opts.outputDir(f'{OUTPUT_FOLDER_PATH}').outputName('test.mp4').format('269')
  opts.subtitlesLang('en').writeSubtitles().embedSubtitle()
  DownloadSection().run(
    url='https://www.youtube.com/watch?v=JMu9kdGHU3A',
    opts=opts
  )

  # check file exist
  assert exists(f'{OUTPUT_FOLDER_PATH}/test.mp4')

  # check subtitle is embeded
  mediaInfo = MediaInfo.parse(f'{OUTPUT_FOLDER_PATH}/test.mp4')
  assert any([track.track_type == 'Text' for track in mediaInfo.tracks])

def test_with_real_download_bili():
  prepare_output_folder()

  opts = Opts().outputDir(f'{OUTPUT_FOLDER_PATH}')
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