from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from typing_extensions import Union

from src.section.FormatSection import FormatSection, LazyFormatSection
from src.service.MetaData import VideoMetaData
from src.structs.video_info import BundledFormat

@patch('builtins.input')
def test_format(input_mock:Mock):
  # [(input_mock_ret, exepected_ret)]
  case_ls = [
    ('auto', 'mp4'),
    ('', 'mp4'),
    ('avc', 'avc')
  ]

  for case in case_ls:
    print('testing', case)
    input_mock_ret, exepected_ret = case

    input_mock.reset_mock()
    
    input_mock.return_value = input_mock_ret
    assert FormatSection().run() == exepected_ret

@patch('src.section.FormatSection.LazyFormatSection._ask_format_option')
def test_lazy_format_main(ask_format_mock:Mock):  
  class fake_videoMd (VideoMetaData):
    def __init__(self, both_ls=[], video_ls=[], audio_ls=[], *args, **kwargs):
      self._format = {
        'both': both_ls,
        'video': video_ls,
        'audio': audio_ls
      }
  
  fake_video_format1 = { 'format_id': 'v1' }
  fake_video_format2 = { 'format_id': 'v2' }
  fake_audio_format = { 'format_id': 'a1' }
  fake_both_format = { 'format_id': 'b1' }
  
  fake_videoMd_md1 = fake_videoMd(video_ls=[fake_video_format1])
  fake_videoMd_md2 = fake_videoMd(video_ls=[fake_video_format1], audio_ls=[fake_audio_format])
  fake_videoMd_md3 = fake_videoMd(video_ls=[fake_video_format1], audio_ls=[fake_audio_format], both_ls=[fake_both_format])
  fake_videoMd_md4 = fake_videoMd(video_ls=[fake_video_format2])
  
  # [(video metadata list, ask_format_mock_ret, exepected_ret list)]
  case_ls : list[tuple[list[fake_videoMd], str, list[Union[str, BundledFormat]]]] = [
    # video format only
    ([fake_videoMd_md1], LazyFormatSection.OPT_QUA_EFF, ['v1']),
    # video and audio format only
    ([fake_videoMd_md2], LazyFormatSection.OPT_QUA_EFF, [BundledFormat('v1', 'a1')]),
    # video, audio and both format. And choose quality-efficient balance
    ([fake_videoMd_md3], LazyFormatSection.OPT_QUA_EFF, ['b1']),
    # video, audio and both format. And choose best quality
    ([fake_videoMd_md3], LazyFormatSection.OPT_BEST_QUA, [BundledFormat('v1', 'a1')]),
    # multiple video metadata
    ([fake_videoMd_md3, fake_videoMd_md4], LazyFormatSection.OPT_QUA_EFF, ['b1', 'v2'])
  ]
  
  for case in case_ls:
    print('testing', case)
    case_md_ls, case_ask_format_mock_ret, case_exepected_ret = case
    
    ask_format_mock.reset_mock()
    ask_format_mock.return_value = case_ask_format_mock_ret

    ret_format_ls = LazyFormatSection().run(case_md_ls)
    
    assert len(ret_format_ls) == len(case_exepected_ret)
    for ret_format, expected_format in zip(ret_format_ls, case_exepected_ret):
      assert ret_format == expected_format
  
@patch('src.section.FormatSection.inq_prompt')
@patch('src.section.FormatSection.get_lyd_format_autofill')
@patch('src.section.FormatSection.LazyFormatSection._get_options')
def test_lazy_format_ask_format(get_options_mock:Mock, autofill_mock:Mock, prompt_mock:Mock):
  """
    Test the function will return the first option if there is only one option
    without asking user
  """  
  # [(fake options, autofill return, prompt return, do autofill called, do prompt called, expected return)]
  case_ls : list[tuple[list[str], int, str, bool, bool, str]] = [
    # only one option
    (
      [LazyFormatSection.OPT_BEST_QUA], None, None,
      False, False, LazyFormatSection.OPT_BEST_QUA
    ),
    # more than one option, and autofill 1
    (
      [LazyFormatSection.OPT_BEST_QUA, LazyFormatSection.OPT_QUA_EFF], 0, None,
      True, False, LazyFormatSection.OPT_BEST_QUA
    ),
    # more than one option, and autofill 2
    (
      [LazyFormatSection.OPT_BEST_QUA, LazyFormatSection.OPT_QUA_EFF], 1, None,
      True, False, LazyFormatSection.OPT_QUA_EFF
    ),
    # more than one option, and prompt
    (
      [LazyFormatSection.OPT_BEST_QUA, LazyFormatSection.OPT_QUA_EFF], None, LazyFormatSection.OPT_BEST_QUA,
      True, True, LazyFormatSection.OPT_BEST_QUA
    )
  ]
  
  for case in case_ls:
    print('testing', case)
    case_options, case_autofill_ret, case_prompt_ret, case_do_autofill, case_do_prompt, case_exepected_ret = case
    
    get_options_mock.reset_mock()
    autofill_mock.reset_mock()
    prompt_mock.reset_mock()
    
    get_options_mock.return_value = case_options
    autofill_mock.return_value = case_autofill_ret
    prompt_mock.return_value = { 'format_option': case_prompt_ret }
    
    res = LazyFormatSection()._ask_format_option([])
    
    assert res == case_exepected_ret
    assert autofill_mock.called == case_do_autofill
    assert prompt_mock.called == case_do_prompt

def test_lazy_format_get_options ():
  class fake_videoMd (VideoMetaData):
    def __init__(self, both_ls=[], video_ls=[], audio_ls=[], *args, **kwargs):
      self._format = {
        'both': both_ls,
        'video': video_ls,
        'audio': audio_ls
      }

  fake_video_format1 = { 'format_id': 'v1' }
  fake_video_format2 = { 'format_id': 'v2' }
  fake_audio_format1 = { 'format_id': 'a1' }
  fake_audio_format2 = { 'format_id': 'a2' }
  fake_both_format = { 'format_id': 'b1' }
  
  fake_videoMd_md1 = fake_videoMd(video_ls=[fake_video_format1], audio_ls=[fake_audio_format1], both_ls=[fake_both_format])
  fake_videoMd_md2 = fake_videoMd(video_ls=[fake_video_format2], audio_ls=[fake_audio_format2])

  # [(list of video md, expected return)]
  case_ls : list[tuple[list[fake_videoMd], list[str]]] = [
    # all format have both
    ([fake_videoMd_md1], [LazyFormatSection.OPT_BEST_QUA, LazyFormatSection.OPT_QUA_EFF]),
    # not all format have both
    ([fake_videoMd_md1, fake_videoMd_md2], [LazyFormatSection.OPT_BEST_QUA])
  ]

  for case in case_ls:
    print('testing', case)
    case_video_md_ls, case_exepected_ret = case    
    assert LazyFormatSection()._get_options(case_video_md_ls) == case_exepected_ret
