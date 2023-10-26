from src.dlConfig import dlConfig, DefaultConfig

def test_dlConfig_init_with_value():
  condig = dlConfig(
    url='https://www.example.com',
    cookieFile='cookies.txt',
    subLang='en', doWriteAutoSub=True,
    outputFormat='mp4', outputDir='/path/to/output', outputName='example', outputExt='.mp4'
  )
  assert condig.url == 'https://www.example.com'
  assert condig.cookieFile == 'cookies.txt'
  assert condig.subLang == 'en'
  assert condig.doWriteAutoSub == True
  assert condig.outputFormat == 'mp4'
  assert condig.outputDir == '/path/to/output'
  assert condig.outputName == 'example'
  assert condig.outputExt == '.mp4'

def test_dlConfig_doWriteSub():
  config = dlConfig()
  assert config.doWriteSub == False

  config.subLang = 'en'
  assert config.doWriteSub == True

def test_dlConfig_overwriteConfigBy():
  config1 = dlConfig()

  config2 = dlConfig()
  config2.url = 'https://www.example.com'
  config2.cookieFile = 'cookies.txt'
  config2.subLang = 'en'
  config2.doWriteAutoSub = True
  config2.outputFormat = 'mp4'
  config2.outputDir = '/path/to/output'
  config2.outputName = 'example'
  config2.outputExt = '.mp4'

  config1.overwriteConfigBy(config2)
  assert config1.url == config2.url
  assert config1.cookieFile == config2.cookieFile
  assert config1.subLang == config2.subLang
  assert config1.doWriteAutoSub == config2.doWriteAutoSub
  assert config1.outputFormat == config2.outputFormat
  assert config1.outputDir == config2.outputDir
  assert config1.outputName == config2.outputName
  assert config1.outputExt == config2.outputExt

def test_dlConfig_fillConfigBy():
  config1 = dlConfig()
  config1.url = 'https://www.example.com'

  config2 = dlConfig()
  config2.url = 'https://www.example2.com'
  config2.cookieFile = 'cookies.txt'
  config2.subLang = 'en'
  config2.doWriteAutoSub = True
  config2.outputFormat = 'mp4'
  config2.outputDir = '/path/to/output'
  config2.outputName = 'example'
  config2.outputExt = '.mp4'

  config1.fillConfigBy(config2)

  assert config1.url == 'https://www.example.com'
  assert config1.cookieFile == config2.cookieFile
  assert config1.subLang == config2.subLang
  assert config1.doWriteAutoSub == config2.doWriteAutoSub
  assert config1.outputFormat == config2.outputFormat
  assert config1.outputDir == config2.outputDir
  assert config1.outputName == config2.outputName
  assert config1.outputExt == config2.outputExt

def test_default():
  config = dlConfig()
  config.default()

  assert config.url == DefaultConfig.url.value
  assert config.cookieFile == DefaultConfig.cookieFile.value
  assert config.subLang == DefaultConfig.subLang.value
  assert config.doWriteAutoSub == DefaultConfig.doWriteAutoSub.value
  assert config.outputFormat == DefaultConfig.outputFormat.value
  assert config.outputDir == DefaultConfig.outputDir.value
  assert config.outputName == DefaultConfig.outputName.value
  assert config.outputExt == DefaultConfig.outputExt.value
