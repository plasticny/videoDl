from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection
from src.service.YtDlpHelper import Opts
from src.service.structs import Subtitle

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

@patch('src.section.SubTitleSection.SubTitleSection.selectWriteSub')
@patch('src.section.SubTitleSection.MetaData.fetchMetaData')
def test_noSubFound(fetch_mock, selectWriteSub_mock):
  class fake_VideoMetaData:
    def __init__(self):
      self.subtitles = []
      self.autoSubtitles = []

  fetch_mock.return_value = fake_VideoMetaData()
  selectWriteSub_mock.return_value = False
  opts = SubTitleSection('').run('',Opts())
  check_opts(opts, False, None, None, None, None)

@patch('src.section.SubTitleSection.SubTitleSection.selectWriteSub')
@patch('src.section.SubTitleSection.MetaData.fetchMetaData')
def test_notWriteSub(fetch_mock, selectWriteSub_mock):
  class fake_VideoMetaData:
    def __init__(self):
      self.subtitles = []
      self.autoSubtitles = [Subtitle('en', 'English')]

  fetch_mock.return_value = fake_VideoMetaData()
  selectWriteSub_mock.return_value = False
  opts = SubTitleSection('').run('',Opts())
  check_opts(opts, False, None, None, None, None)

@patch('src.section.SubTitleSection.MetaData.fetchMetaData')
@patch('src.section.SubTitleSection.inq_prompt')
def test_full_run(prompt_mock, fetch_mock):
  """
    Test with a full run
    and check if the passed opts is not changed
  """
  class fake_VideoMetaData:
    def __init__(self):
      self.subtitles = []
      self.autoSubtitles = [Subtitle('en', 'English', True)]

  opts = Opts()
  backup_opts = opts.copy()

  prompt_mock.side_effect = [
    {'writeSub': 'Yes'},
    {
      'lang': Subtitle('en', 'English', True),
      'writeMode': ['Embed', 'Burn'],
      'writeAutoSub': 'Yes'
    }
  ]
  fetch_mock.return_value = fake_VideoMetaData()
  ret_opts = SubTitleSection('').run('',opts)

  # passed opts should not be changed
  assert opts == backup_opts

  # check returned opts
  check_opts(ret_opts, False, True, 'en', True, True)