from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection
from src.service.YtDlpHelper import Opts
from src.service.structs import Subtitle
from src.service.MetaData import VideoMetaData, PlaylistMetaData

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

def test_playlist():
  class fake_PlaylistMetaData(PlaylistMetaData):
    def __init__(self):
      pass

  opts = SubTitleSection('').run(fake_PlaylistMetaData())
  check_opts(opts, False, None, None, None, None)

@patch('src.section.SubTitleSection.SubTitleSection.selectWriteSub')
def test_noSubFound(selectWriteSub_mock):
  class fake_VideoMetaData(VideoMetaData):
    def __init__(self):
      self._sub = []
      self._auto_sub = []

  selectWriteSub_mock.return_value = False
  opts = SubTitleSection('').run(fake_VideoMetaData())
  check_opts(opts, False, None, None, None, None)

@patch('src.section.SubTitleSection.SubTitleSection.selectWriteSub')
def test_notWriteSub(selectWriteSub_mock):
  class fake_VideoMetaData(VideoMetaData):
    def __init__(self):
      self._sub = []
      self._auto_sub = [Subtitle('en', 'English')]

  selectWriteSub_mock.return_value = False
  opts = SubTitleSection('').run(fake_VideoMetaData())
  check_opts(opts, False, None, None, None, None)

@patch('src.section.SubTitleSection.inq_prompt')
def test_full_run(prompt_mock):
  """
    Test with a full run
    and check if the passed opts is not changed
  """
  class fake_VideoMetaData(VideoMetaData):
    def __init__(self):
      self._sub = []
      self._auto_sub = [Subtitle('en', 'English', True)]

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
  ret_opts = SubTitleSection('').run(fake_VideoMetaData(),opts)

  # passed opts should not be changed
  assert opts == backup_opts

  # check returned opts
  check_opts(ret_opts, False, True, 'en', True, True)