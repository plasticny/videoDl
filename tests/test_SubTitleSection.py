from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection, VALUE
from src.service.YtDlpHelper import Opts

@patch('builtins.input', return_value='N')
def test_noWriteSub(_):
  section = SubTitleSection('')

  opts = section.run(Opts())
  assert opts()['writesubtitles'] == False
  assert opts()['writeautomaticsub'] == None
  assert opts()['subtitleslangs'] == [None]

@patch('builtins.input')
def test_subLang(input_mock):
  section = SubTitleSection('')

  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'N']
  opts = section.run(Opts())
  assert opts()['writesubtitles'] == True
  assert opts()['writeautomaticsub'] == False
  assert opts()['subtitleslangs'] == ['zh']

  # Test with default language
  input_mock.side_effect = ['Y','', 'N']
  opts = section.run(Opts())
  assert opts()['writesubtitles'] == True
  assert opts()['writeautomaticsub'] == False
  assert opts()['subtitleslangs'] == [VALUE.DEFAULT_IN_LANG.value]

@patch('builtins.input')
def test_doWriteAutoSub(input_mock):
  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'Y']
  opts = SubTitleSection('').run(Opts())
  assert opts()['writesubtitles'] == True
  assert opts()['writeautomaticsub'] == True
  assert opts()['subtitleslangs'] == ['zh']

@patch('builtins.input')
def test_not_change_param_opts(input_mock):
  opts = Opts()
  backup_opts = opts.copy()

  input_mock.side_effect = ['Y', 'zh', 'Y']
  SubTitleSection('').run(opts)
  assert opts == backup_opts