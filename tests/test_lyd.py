from unittest.mock import patch, Mock

from uuid import uuid4

from tests.testFileHelper import prepare_output_folder

from src.lazyYtDownload import login, configDownload, run
from src.dlConfig import dlConfig, DefaultConfig

# test login function
@patch('src.lazyYtDownload.LoginSection.run')
def test_login(login_mock):
  config = dlConfig()

  login_mock.return_value = 'cookie'

  # test other
  config.url = 'other'
  assert login(config) == DefaultConfig.cookieFile.value
  login_mock.assert_not_called()

  # test bilibili
  config.url = 'www.bilibili.com/video/BV1QK4y1d7dQ'
  assert login(config) == 'cookie'
  login_mock.assert_called_once()

# test configDownload function
@patch('src.lazyYtDownload.uuid4')
@patch('src.lazyYtDownload.SetUpDownloadSection.run')
@patch('src.lazyYtDownload.login')
@patch('src.lazyYtDownload.UrlSection.run')
@patch('src.lazyYtDownload.ListSubtitleSection.run', Mock)
def test_configDownlaod(url_mock, login_mock, setup_mock, uuid_mock):
  url_mock.return_value = 'url'
  login_mock.return_value = 'cookie'
  setup_mock.return_value = dlConfig(
    subLang='en', doWriteAutoSub=True,
    outputDir='outputDir'
  )
  uuid_mock.return_value = 'outputName'

  config = configDownload()
  
  assert config.url == 'url'
  assert config.cookieFile == 'cookie'
  assert config.subLang == 'en'
  assert config.doWriteAutoSub == True
  assert config.outputDir == 'outputDir'
  assert config.outputName == 'outputName'

# test with download a video
@patch('src.lazyYtDownload.configDownload')
def test_with_download(config_mock):
  prepare_output_folder()

  config = dlConfig()
  config.default()
  config.url = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  config.cookieFile = ''
  config.outputDir = 'tests/testFiles/output'
  config.outputName = uuid4()

  config_mock.return_value = config

  run(loop=False)