from unittest.mock import patch
from src.section.SetUpDownloadSection import SetUpDownloadSection
from src.dlConfig import dlConfig

@patch('src.section.SetUpDownloadSection.SubTitleSection')
@patch('src.section.SetUpDownloadSection.FormatSection')
@patch('src.section.SetUpDownloadSection.OutputSection')
def test_not_ask_all(sub_mock, format_mock, output_mock):
  config = dlConfig()
  result_config = SetUpDownloadSection(
    title='',
    config=dlConfig(),
    subtitle=False, format=False, outputDir=False, outputName=False,
  ).run()

  assert sub_mock.called == False
  assert format_mock.called == False
  assert output_mock.called == False

  # check if config is not changed
  assert config.subLang == result_config.subLang
  assert config.doWriteAutoSub == result_config.doWriteAutoSub
  assert config.outputFormat == result_config.outputFormat
  assert config.outputDir == result_config.outputDir
  assert config.outputName == result_config.outputName

@patch('src.section.SetUpDownloadSection.SubTitleSection')
def test_ask_subtitle(sub_mock):
  sub_mock.return_value.run.return_value = ('en', True)

  result_config = SetUpDownloadSection(
    title='',
    config=dlConfig(),
    subtitle=True, format=False, outputDir=False, outputName=False,
  ).run()

  assert sub_mock.called == True
  assert result_config.subLang == 'en'
  assert result_config.doWriteAutoSub == True

@patch('src.section.SetUpDownloadSection.FormatSection')
def test_ask_format(format_mock):
  format_mock.return_value.run.return_value = 'mp4'

  result_config = SetUpDownloadSection(
    title='',
    config=dlConfig(),
    subtitle=False, format=True, outputDir=False, outputName=False,
  ).run()

  assert format_mock.called == True
  assert result_config.outputFormat == 'mp4'

@patch('src.section.SetUpDownloadSection.OutputSection')
def test_ask_output_dir(output_mock):
  output_mock.return_value.run.return_value = ('/home', None)

  result_config = SetUpDownloadSection(
    title='',
    config=dlConfig(),
    subtitle=False, format=False, outputDir=True, outputName=False,
  ).run()

  assert output_mock.called == True
  assert result_config.outputDir == '/home'
  assert result_config.outputName == None

@patch('src.section.SetUpDownloadSection.OutputSection')
def test_ask_output_name(output_mock):
  output_mock.return_value.run.return_value = (None, 'video')

  result_config = SetUpDownloadSection(
    title='',
    config=dlConfig(),
    subtitle=False, format=False, outputDir=False, outputName=True,
  ).run()

  assert output_mock.called == True
  assert result_config.outputDir == None
  assert result_config.outputName == 'video'