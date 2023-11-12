from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection, VALUE
from src.service.YtDlpHelper import Opts

@patch('builtins.input', return_value='N')
def test_noWriteSub(_):
  section = SubTitleSection('')

  opts = section.run(Opts())
  assert opts.writeSubtitles == False
  assert opts.writeAutomaticSub == None
  assert opts.subtitlesLang == None
  assert opts.embedSubtitle == None

@patch('builtins.input')
def test_subLang(input_mock):
  section = SubTitleSection('')

  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'N', 'N']
  opts = section.run(Opts())
  assert opts.writeSubtitles == True
  assert opts.writeAutomaticSub == False
  assert opts.subtitlesLang == 'zh'
  assert opts.embedSubtitle == False

  # Test with default language
  input_mock.side_effect = ['Y','', 'N', 'N']
  opts = section.run(Opts())
  assert opts.writeSubtitles == True
  assert opts.writeAutomaticSub == False
  assert opts.subtitlesLang == VALUE.DEFAULT_IN_LANG.value
  assert opts.embedSubtitle == False

@patch('builtins.input')
def test_doWriteAutoSub(input_mock):
  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'Y', 'N']
  opts = SubTitleSection('').run(Opts())
  assert opts.writeSubtitles == True
  assert opts.writeAutomaticSub == True
  assert opts.subtitlesLang == 'zh'
  assert opts.embedSubtitle == False

@patch('builtins.input')
def test_embedSubtitle(input_mock):
  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'Y', 'Y']
  opts = SubTitleSection('').run(Opts())
  assert opts.writeSubtitles == True
  assert opts.writeAutomaticSub == True
  assert opts.subtitlesLang == 'zh'
  assert opts.embedSubtitle == True

@patch('builtins.input')
def test_not_change_param_opts(input_mock):
  opts = Opts()
  backup_opts = opts.copy()

  input_mock.side_effect = ['Y', 'zh', 'Y', 'Y']
  SubTitleSection('').run(opts)
  assert opts == backup_opts