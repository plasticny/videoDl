from sys import path as sys_path
sys_path.append('src')

from pytest import raises as pytest_raises

from src.service.YtDlpHelper import CommandConverter
from src.dlConfig import dlConfig

def test_url():
  config = dlConfig()

  # when url is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.url
  assert str(e_info.value) == 'url is not set'

  # when url is set empty
  config.url = ''
  converter = CommandConverter(config)
  assert converter.url == ''

  # when url is set
  config.url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  converter = CommandConverter(config)
  assert converter.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def test_cookies():
  config = dlConfig()

  # when cookieFile is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.cookies
  assert str(e_info.value) == 'cookieFile is not set'

  # when cookieFile is set empty
  config.cookieFile = ''
  converter = CommandConverter(config)
  assert converter.cookies == ''

  # when cookieFile is set
  config.cookieFile = 'cookies.txt'
  converter = CommandConverter(config)
  assert converter.cookies == '--cookies cookies.txt'

def test_embedSubs():
  config = dlConfig()

  # when subLang is not set
  converter = CommandConverter(config)
  assert converter.embedSubs == ''

  # when subLang is set
  config.subLang = 'en'
  converter = CommandConverter(config)
  assert converter.embedSubs == '--embed-subs'

def test_subLang():
  config = dlConfig()

  # when subLang is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.subLang
  assert str(e_info.value) == 'subLang is not set'

  # when subLang is set empty
  config.subLang = ''
  converter = CommandConverter(config)
  assert converter.subLang == ''

  # when subLang is set
  config.subLang = 'en'
  converter = CommandConverter(config)
  assert converter.subLang == '--sub-lang en'

def test_writeAutoSubs():
  config = dlConfig()

  # when doWriteAutoSub is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.writeAutoSubs
  assert str(e_info.value) == 'doWriteAutoSub is not set'

  # when doWriteSub is False
  config.doWriteAutoSub = True
  converter = CommandConverter(config)
  assert converter.writeAutoSubs == ''

  # when doWriteSub is True and doWriteAutoSub is False
  config.subLang = 'en'
  config.doWriteAutoSub = False
  converter = CommandConverter(config)
  assert converter.writeAutoSubs == ''

  # when doWriteSub is True and doWriteAutoSub is True
  config.doWriteAutoSub = True
  converter = CommandConverter(config)
  assert converter.writeAutoSubs == '--write-auto-subs'

def test_outputName():
  config = dlConfig()

  # when outputName is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.outputName
  assert str(e_info.value) == 'outputName is not set'

  # when outputName is set empty
  config.outputName = ''
  converter = CommandConverter(config)
  assert converter.outputName == ''

  # when outputName is set
  config.outputName = 'test'
  converter = CommandConverter(config)
  assert converter.outputName == '-o test.%(ext)s'

def test_outputDir():
  config = dlConfig()

  # when outputDir is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.outputDir
  assert str(e_info.value) == 'outputDir is not set'

  # when outputDir is set empty
  config.outputDir = ''
  converter = CommandConverter(config)
  assert converter.outputDir == ''

  # when outputDir is set
  config.outputDir = 'test'
  converter = CommandConverter(config)
  assert converter.outputDir == '-P test'

def test_outputFormat():
  config = dlConfig()

  # when outputFormat is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.outputFormat
  assert str(e_info.value) == 'outputFormat is not set'

  # when outputFormat is set empty
  config.outputFormat = ''
  converter = CommandConverter(config)
  assert converter.outputFormat == ''

  # when outputFormat is set
  config.outputFormat = 'bestvideo+bestaudio'
  converter = CommandConverter(config)
  assert converter.outputFormat == '-f bestvideo+bestaudio'

def test_listFormat():
  config = dlConfig()

  # when url is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.listFormat
  assert str(e_info.value) == 'url is not set'

  # when url is set empty
  config.url = ''
  converter = CommandConverter(config)
  assert converter.listFormat == ''

  # when url is set
  config.url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
  converter = CommandConverter(config)
  assert converter.listFormat == '--list-formats https://www.youtube.com/watch?v=dQw4w9WgXcQ'

def test_listSubs():
  config = dlConfig()

  # when url is not set
  converter = CommandConverter(config)
  with pytest_raises(Exception) as e_info:
    converter.listSubs
  assert str(e_info.value) == 'url is not set'

  # when url is set empty
  config.url = ''
  converter = CommandConverter(config)
  assert converter.listSubs == ''

  # when url is set
  config.url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
  converter = CommandConverter(config)
  assert converter.listSubs == '--list-subs https://www.youtube.com/watch?v=dQw4w9WgXcQ'