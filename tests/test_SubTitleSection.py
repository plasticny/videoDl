from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection
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

@patch('src.section.SubTitleSection.inq_prompt')
def test_noWriteSub(prompt_mock):
  prompt_mock.return_value = {'choice': 'No'}
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, False, None, None, None, None)

@patch('src.section.SubTitleSection.inq_prompt')
def test_subLang(prompt_mock):
  section = SubTitleSection('')

  # Test with custom language
  prompt_mock.side_effect = [
    {'choice': 'Yes'},
    {
      'lang': 'zh',
      'writeMode': [],
      'writeAutoSub': 'No'
    }
  ]
  opts = section.run(Opts())
  check_opts(opts, True, False, 'zh', False, False)

  # Test with default language
  prompt_mock.side_effect = [
    {'choice': 'Yes'},
    {
      'lang': '',
      'writeMode': [],
      'writeAutoSub': 'No'
    }
  ]
  opts = section.run(Opts())
  check_opts(opts, True, False, 'en', False, False)

@patch('src.section.SubTitleSection.inq_prompt')
def test_doWriteAutoSub(prompt_mock):
  prompt_mock.side_effect = [
    {'choice': 'Yes'},
    {
      'lang': 'zh',
      'writeMode': [],
      'writeAutoSub': 'Yes'
    }
  ]
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, True, True, 'zh', False, False)

@patch('src.section.SubTitleSection.inq_prompt')
def test_embedSubtitle(prompt_mock):
  prompt_mock.side_effect = [
    {'choice': 'Yes'},
    {
      'lang': 'zh',
      'writeMode': ['Embed'],
      'writeAutoSub': 'Yes'
    }
  ]
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, True, True, 'zh', True, False)

@patch('src.section.SubTitleSection.inq_prompt')
def test_burnSubtitle(prompt_mock):
  prompt_mock.side_effect = [
    {'choice': 'Yes'},
    {
      'lang': 'zh',
      'writeMode': ['Embed', 'Burn'],
      'writeAutoSub': 'Yes'
    }
  ]
  opts = SubTitleSection('').run(Opts())
  check_opts(opts, True, True, 'zh', True, True)

@patch('src.section.SubTitleSection.inq_prompt')
def test_not_change_param_opts(prompt_mock):
  opts = Opts()
  backup_opts = opts.copy()

  prompt_mock.side_effect = [
    {'choice': 'Yes'},
    {
      'lang': 'zh',
      'writeMode': ['Embed', 'Burn'],
      'writeAutoSub': 'Yes'
    }
  ]
  SubTitleSection('').run(opts)
  assert opts == backup_opts