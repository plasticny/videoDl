from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection, VALUE
from src.service.YtDlpHelper import Opts

def check_opts(
    opts:Opts,
    expected_ws:bool, expected_was:bool, expected_lang:str, 
    expected_embed:bool, expected_burn:bool
  ):
  """
    Helper function for checking subtitle options in opts

    Args hints:
      `ws`: writeSubtitles\n
      `was`: writeAutomaticSub\n
      `lang`: subtitlesLang\n
      `embed`: embedSubtitle\n
      `burn`: burnSubtitle
  """
  assert opts.writeSubtitles == expected_ws
  assert opts.writeAutomaticSub == expected_was
  assert opts.subtitlesLang == expected_lang
  assert opts.embedSubtitle == expected_embed
  assert opts.burnSubtitle == expected_burn

@patch('builtins.input', return_value='N')
def test_noWriteSub(_):
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, False, None, None, None, None)

@patch('builtins.input')
def test_subLang(input_mock):
  section = SubTitleSection('')

  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'N', 'N', 'N']
  opts = section.run(Opts())
  check_opts(opts, True, False, 'zh', False, False)

  # Test with default language
  input_mock.side_effect = ['Y','', 'N', 'N', 'N']
  opts = section.run(Opts())
  check_opts(opts, True, False, VALUE.DEFAULT_IN_LANG.value, False, False)

@patch('builtins.input')
def test_doWriteAutoSub(input_mock):
  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'Y', 'N', 'N']
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, True, True, 'zh', False, False)

@patch('builtins.input')
def test_embedSubtitle(input_mock):
  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'Y', 'Y', 'N']
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, True, True, 'zh', True, False)

@patch('builtins.input')
def test_burnSubtitle(input_mock):
  # Test with custom language
  input_mock.side_effect = ['Y','zh', 'Y', 'Y', 'Y']
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, True, True, 'zh', True, True)

@patch('builtins.input')
def test_not_change_param_opts(input_mock):
  opts = Opts()
  backup_opts = opts.copy()

  input_mock.side_effect = ['Y', 'zh', 'Y', 'Y', 'Y']
  SubTitleSection('').run(opts)
  assert opts == backup_opts