from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from src.section.FormatSection import FormatSection, LazyFormatSection
from src.service.MetaData import VideoMetaData
from src.structs.video_info import BundledFormat

@patch('builtins.input')
def test_with_auto_format(input_mock:Mock):
  section = FormatSection()

  input_mock.return_value = 'auto'
  assert section.run() == 'mp4'

  input_mock.return_value = ''
  assert section.run() == 'mp4'

@patch('src.section.FormatSection.LazyFormatSection._ask_format_option')
def test_lazy_format_main(ask_format_mock:Mock):
  section = LazyFormatSection()
  
  class fake_videoMd (VideoMetaData):
    def __init__(self, fake_formats, *args, **kwargs):
      self._format = fake_formats
  
  # === test when there is video only === #
  md_ls = [
    fake_videoMd({
      'both': [],
      'video': [
        { 'format_id': 'v1' },
      ],
      'audio': []
    })
  ]
  ask_format_mock.return_value = LazyFormatSection.OPT_QUA_EFF
  assert section.run(md_ls) == ['v1']
  
  # === test when these is no both but there is audio === #
  md_ls = [
    fake_videoMd({
      'both': [],
      'video': [
        { 'format_id': 'v1' },
      ],
      'audio': [
        { 'format_id': 'a1' },
      ]
    })
  ]
  ask_format_mock.return_value = LazyFormatSection.OPT_QUA_EFF
  ret_format_ls = section.run(md_ls)
  assert len(ret_format_ls) == 1
  ret_bundled_format = ret_format_ls[0]
  assert isinstance(ret_bundled_format, BundledFormat)
  assert ret_bundled_format.video == 'v1'
  assert ret_bundled_format.audio == 'a1'
  
  # === test when there is both === #
  md_ls = [
    fake_videoMd({
      'both': [
        { 'format_id': 'b1' },
      ],
      'video': [
        { 'format_id': 'v1' },
      ],
      'audio': [
        { 'format_id': 'a1' },
      ]
    })
  ]
  # use quality-efficient balance
  ask_format_mock.return_value = LazyFormatSection.OPT_QUA_EFF
  assert section.run(md_ls) == ['b1']
  # use best quality
  ask_format_mock.return_value = LazyFormatSection.OPT_BEST_QUA
  ret_format_ls = section.run(md_ls)
  assert len(ret_format_ls) == 1
  ret_bundled_format = ret_format_ls[0]
  assert isinstance(ret_bundled_format, BundledFormat)
  assert ret_bundled_format.video == 'v1'
  assert ret_bundled_format.audio == 'a1'
  
  # === test when there is multiple metadata === #
  md_ls = [
    fake_videoMd({
      'both': [
        { 'format_id': 'b1' },
      ],
      'video': [
        { 'format_id': 'v1' },
      ],
      'audio': [
        { 'format_id': 'a1' },
      ]
    }),
    fake_videoMd({
      'both': [],
      'video': [
        { 'format_id': 'v2' },
      ],
      'audio': []
    })
  ]
  ask_format_mock.return_value = LazyFormatSection.OPT_QUA_EFF
  assert section.run(md_ls) == ['b1', 'v2']
  
@patch('src.section.FormatSection.inq_prompt')
@patch('src.section.FormatSection.LazyFormatSection._get_options')
def test_lazy_format_ask_format(get_options_mock:Mock, prompt_mock:Mock):
  """
    Test the function will return the first option if there is only one option
    without asking user
  """
  section = LazyFormatSection()
  prompt_mock.return_value = { 'format_option': '' }
  
  get_options_mock.return_value = [LazyFormatSection.OPT_BEST_QUA]
  section._ask_format_option([])
  assert len(prompt_mock.mock_calls) == 0
  
  prompt_mock.reset_mock()
  get_options_mock.return_value = [LazyFormatSection.OPT_BEST_QUA, LazyFormatSection.OPT_QUA_EFF]
  section._ask_format_option([])
  assert len(prompt_mock.mock_calls) == 1

def test_lazy_format_get_options ():
  class fake_videoMd (VideoMetaData):
    def __init__ (self, fake_formats, *args, **kwargs):
      self._format = fake_formats
  
  section = LazyFormatSection()

  # test all format have both
  md_ls = [
    fake_videoMd({
      'both': [
        { 'format_id': 'b1' },
      ],
      'video': [
        { 'format_id': 'v1' },
      ],
      'audio': [
        { 'format_id': 'a1' },
      ]
    }),
  ]
  assert section._get_options(md_ls) == [
    LazyFormatSection.OPT_BEST_QUA,
    LazyFormatSection.OPT_QUA_EFF
  ]
  
  # test not all format have both
  md_ls = [
    fake_videoMd({
      'both': [],
      'video': [
        { 'format_id': 'v1' },
      ],
      'audio': [
        { 'format_id': 'a1' },
      ]
    }),
    fake_videoMd({
      'both': [
        { 'format_id': 'b1' },
      ],
      'video': [
        { 'format_id': 'v2' },
      ],
      'audio': [
        { 'format_id': 'a2' },
      ]
    })
  ]
  assert section._get_options(md_ls) == [LazyFormatSection.OPT_BEST_QUA]
