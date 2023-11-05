from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch, ANY
from pytest import raises as pytest_raises
from os.path import exists

from tests.fakers import fake_CompletedProcess
from tests.testFileHelper import prepare_output_folder

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

  opts = Opts().outputDir('tests/testFiles/output').outputName('test.mp4').format('269')
  DownloadSection().run(
    url='https://www.youtube.com/watch?v=JMu9kdGHU3A',
    opts=opts
  )

  assert exists('tests/testFiles/output/test.mp4')

def test_with_real_download_bili():
  prepare_output_folder()

  opts = Opts().outputDir('tests/testFiles/output')
  DownloadSection().run(
    url='https://www.bilibili.com/video/BV1154y1T765',
    opts=opts
  )

  assert exists('tests/testFiles/output/小 僧 觉 得 很 痛 [BV1154y1T765].mp4')

@patch('src.section.DownloadSection.YoutubeDL.download')
def test_not_change_param_opts(_):
  opts = Opts()
  backup_opts = opts.copy()
  DownloadSection().run('url', opts)
  assert opts == backup_opts