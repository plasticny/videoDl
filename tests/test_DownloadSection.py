from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch, ANY
from pytest import raises as pytest_raises
from os import remove
from os.path import exists

from tests.fakers import fake_CommandConverter
from tests.testFileHelper import prepare_output_folder

from src.section.DownloadSection import DownloadSection
from src.dlConfig import dlConfig
from src.service.commandUtils import YT_EXEC

@patch('src.section.DownloadSection.runCommand')
@patch('src.section.DownloadSection.CommandConverter')
def test_with_success_mock(cc_mock, runCommand_mock):
  config = dlConfig()
  section = DownloadSection('Download', config)

  fake_cc = fake_CommandConverter(config)
  cc_mock.return_value = fake_cc
  runCommand_mock.return_value = 0

  section.run()

  # check if CommandConverter is called with config
  cc_mock.assert_called_with(section.config)
  
  # check if runCommand is called with YT_EXEC and CommandConverter's properties
  runCommand_mock.assert_called_with(
    execCommand=YT_EXEC,
    paramCommands=[
      fake_cc.url,
      fake_cc.outputName,
      fake_cc.outputDir,
      fake_cc.outputFormat,
      fake_cc.noLiveChat,
      fake_cc.embedSubs,
      fake_cc.writeAutoSubs,
      fake_cc.subLang,
      fake_cc.cookies
    ],
    printCommand=ANY
  )

@patch('src.section.DownloadSection.runCommand')
@patch('src.section.DownloadSection.CommandConverter')
def test_with_fail_mock(cc_mock, runCommand_mock):
  config = dlConfig()
  section = DownloadSection('Download', config, retry=2)

  fake_cc = fake_CommandConverter(config)
  cc_mock.return_value = fake_cc
  runCommand_mock.return_value = 1

  with pytest_raises(Exception) as excinfo:
    section.run()
  
  # check if runCommand is called 3 times
  assert runCommand_mock.call_count == 3
  assert excinfo.type == Exception

def test_with_real_download():
  prepare_output_folder()

  config = dlConfig()
  config.url = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  config.outputName = 'test'
  config.outputDir = 'tests/testFiles/output'
  config.outputFormat = '269'
  config.doWriteAutoSub = False
  config.subLang = ''
  config.cookieFile = ''

  DownloadSection('Download', config).run()

  assert exists('tests/testFiles/output/test.mp4')