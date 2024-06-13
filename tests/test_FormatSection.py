from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from typing_extensions import Union
from dataclasses import dataclass

from src.section.FormatSection import FormatSection
from src.section.FormatSection import LazyFormatSection, LazyFormatSelector, LazyMediaSelector
from src.section.FormatSection import LazyFormatType, LazyMediaType, LazyFormatSectionRet
from src.service.MetaData import VideoMetaData
from src.structs.video_info import BundledFormat


# ======= helper ========= #
class fake_videoMd (VideoMetaData):
  def __init__(self, both_ls=[], video_ls=[], audio_ls=[], *args, **kwargs):
    self._format = {
      'both': both_ls,
      'video': video_ls,
      'audio': audio_ls
    }
    
  @property
  def title (self) -> str:
    return ''

def create_fake_format (format_id:str):
  return { 'format_id': format_id }

def create_fake_video_format (format_id:str, width:int, height:int):
  format = create_fake_format(format_id)
  return { **format, 'width': width, 'height': height }
# ======= helper ========= #


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

@patch('src.section.FormatSection.LazyFormatSection._best_audio')
@patch('src.section.FormatSection.LazyFormatSection._best_quality')
@patch('src.section.FormatSection.LazyFormatSection._quality_efficient')
@patch('src.section.FormatSection.LazyMediaSelector._ask_media')
@patch('src.section.FormatSection.LazyFormatSelector._ask_format_option')
def test_lazy_format_main(
    ask_format_mock:Mock, ask_media_mock : Mock,
    quality_efficient_mock:Mock, best_quality_mock:Mock, best_audio_mock:Mock
  ):
  @dataclass
  class Case:
    md_ls : list[VideoMetaData]
    media : str
    format : str
    expected_media_ret : str
    expected_format_ret : str
  
  quality_efficient_ret = 'v1'
  best_quality_ret = 'v2'
  best_audio_ret = 'a1'
  
  quality_efficient_mock.return_value = quality_efficient_ret
  best_quality_mock.return_value = best_quality_ret
  best_audio_mock.return_value = best_audio_ret
  
  fake_md = fake_videoMd()
  video = LazyMediaType.VIDEO.value
  audio = LazyMediaType.AUDIO.value
  
  case_ls : list[Case] = [
    # video
    # quality-efficient
    Case(
      md_ls=[fake_md],
      media=video, format=LazyFormatType.QUALITY_EFFICIENT.value,
      expected_media_ret=video, expected_format_ret=quality_efficient_ret
    ),
    # best quality
    Case(
      md_ls=[fake_md],
      media=video, format=LazyFormatType.BEST_QUALITY.value,
      expected_media_ret=video, expected_format_ret=best_quality_ret
    ),
    # best quality lowest size
    Case(
      md_ls=[fake_md],
      media=video, format=LazyFormatType.BEST_QUALITY_LOW_SIZE.value,
      expected_media_ret=video, expected_format_ret=best_quality_ret
    ),
    # audio
    Case(
      md_ls=[fake_md],
      media=audio, format=LazyFormatType.BEST_QUALITY.value,
      expected_media_ret=audio, expected_format_ret=best_audio_ret
    )
  ]
  
  for case in case_ls:
    print('testing', case)
    
    ask_format_mock.reset_mock()
    ask_media_mock.reset_mock()
    ask_format_mock.return_value = case.format
    ask_media_mock.return_value = case.media

    ret : LazyFormatSectionRet = LazyFormatSection().run(case.md_ls)
    
    assert ret.media == case.expected_media_ret
    assert ret.format_ls == [case.expected_format_ret]

def test_lazy_format_quality_efficient ():
  fake_both_format = create_fake_format('b1')
  fake_video_format = create_fake_format('v1')
  fake_audio_format = create_fake_format('a1')
  
  fake_md1 = fake_videoMd(video_ls=[fake_video_format], audio_ls=[fake_audio_format], both_ls=[fake_both_format])
  fake_md2 = fake_videoMd(video_ls=[fake_video_format])
  fake_md3 = fake_videoMd(video_ls=[fake_video_format], audio_ls=[fake_audio_format])
  
  # [(video metadata, expected return)]
  case_ls : list[tuple[fake_videoMd, Union[str, BundledFormat]]] = [
    # both format
    (fake_md1, 'b1'),
    # video format only
    (fake_md2, 'v1'),
    # video and audio format only
    (fake_md3, BundledFormat('v1', 'a1'))
  ]
  for case in case_ls:
    print('testing', case)
    case_md, case_exepected_ret = case
    assert LazyFormatSection()._quality_efficient(case_md) == case_exepected_ret
    
def test_lazy_format_best_quality ():
  fake_audio_format = create_fake_format('a1')
  fake_video_format1 = create_fake_video_format('v1', 1920, 1080)
  fake_video_format2 = create_fake_video_format('v2', 1920, 1080)
  fake_video_format3 = create_fake_video_format('v3', 1280, 720)
  
  fake_md1 = fake_videoMd(video_ls=[fake_video_format1], audio_ls=[fake_audio_format])
  fake_md2 = fake_videoMd(video_ls=[fake_video_format1])
  fake_md3 = fake_videoMd(video_ls=[fake_video_format1, fake_video_format2, fake_video_format3])
  
  # [(video metadata, format option, expected return)]
  case_ls : list[tuple[fake_videoMd, str, Union[str, BundledFormat]]] = [
    # best quality
    (fake_md1, LazyFormatType.BEST_QUALITY.value, BundledFormat('v1', 'a1')),
    (fake_md2, LazyFormatType.BEST_QUALITY.value, 'v1'),
    (fake_md3, LazyFormatType.BEST_QUALITY.value, 'v1'),
    # best quality lowest size
    (fake_md3, LazyFormatType.BEST_QUALITY_LOW_SIZE.value, 'v2')
  ]
  for case in case_ls:
    print('testing', case)
    case_md, case_format_option, case_exepected_ret = case
    assert LazyFormatSection()._best_quality(case_md, case_format_option) == case_exepected_ret
  
  
# ======================== LazyFormatSelector ======================== #
@patch('src.section.FormatSection.inq_prompt')
@patch('src.section.FormatSection.get_lyd_format_autofill')
@patch('src.section.FormatSection.LazyFormatSelector._get_options')
def test_lazy_format_ask_format(get_options_mock:Mock, autofill_mock:Mock, prompt_mock:Mock):
  """
    Test the function will return the first option if there is only one option
    without asking user
  """  
  # [(fake options, media, autofill return, prompt return, do autofill called, do prompt called, expected return)]
  case_ls : list[tuple[list[str], str, int, str, bool, bool, str]] = [
    # only one option
    (
      [LazyFormatType.BEST_QUALITY.value], 'Video', None, None,
      False, False, LazyFormatType.BEST_QUALITY.value
    ),
    # more than one option, and autofill 1
    (
      [LazyFormatType.BEST_QUALITY.value, LazyFormatType.QUALITY_EFFICIENT.value], 'Video', 0, None,
      True, False, LazyFormatType.BEST_QUALITY.value
    ),
    # more than one option, and autofill 2
    (
      [LazyFormatType.BEST_QUALITY.value, LazyFormatType.QUALITY_EFFICIENT.value], 'Video', 1, None,
      True, False, LazyFormatType.QUALITY_EFFICIENT.value
    ),
    # more than one option, and prompt
    (
      [LazyFormatType.BEST_QUALITY.value, LazyFormatType.QUALITY_EFFICIENT.value], 'Video', None, LazyFormatType.BEST_QUALITY.value,
      True, True, LazyFormatType.BEST_QUALITY.value
    ),
    # audio
    (
      [], 'Audio', None, None,
      False, False, LazyFormatType.BEST_QUALITY.value
    )
  ]
  
  for case in case_ls:
    print('testing', case)
    case_options, case_media, case_autofill_ret, case_prompt_ret, case_do_autofill, case_do_prompt, case_exepected_ret = case
    
    get_options_mock.reset_mock()
    autofill_mock.reset_mock()
    prompt_mock.reset_mock()
    
    get_options_mock.return_value = case_options
    autofill_mock.return_value = case_autofill_ret
    prompt_mock.return_value = { 'format_option': case_prompt_ret }
    
    res = LazyFormatSelector()._ask_format_option([], case_media)
    
    assert res == case_exepected_ret
    assert autofill_mock.called == case_do_autofill
    assert prompt_mock.called == case_do_prompt

def test_lazy_format_get_options ():
  fake_video_format1 = create_fake_format('v1')
  fake_video_format2 = create_fake_format('v2')
  fake_audio_format1 = create_fake_format('a1')
  fake_audio_format2 = create_fake_format('a2')
  fake_both_format = create_fake_format('b1')
  
  fake_videoMd_md1 = fake_videoMd(video_ls=[fake_video_format1], audio_ls=[fake_audio_format1], both_ls=[fake_both_format])
  fake_videoMd_md2 = fake_videoMd(video_ls=[fake_video_format2], audio_ls=[fake_audio_format2])

  # [(list of video md, expected return)]
  case_ls : list[tuple[list[fake_videoMd], list[str]]] = [
    # all format have both
    ([fake_videoMd_md1], [LazyFormatType.BEST_QUALITY.value, LazyFormatType.BEST_QUALITY_LOW_SIZE.value, LazyFormatType.QUALITY_EFFICIENT.value]),
    # not all format have both
    ([fake_videoMd_md1, fake_videoMd_md2], [LazyFormatType.BEST_QUALITY.value, LazyFormatType.BEST_QUALITY_LOW_SIZE.value])
  ]

  for case in case_ls:
    print('testing', case)
    case_video_md_ls, case_exepected_ret = case    
    assert LazyFormatSelector()._get_options(case_video_md_ls) == case_exepected_ret
# ======================== LazyFormatSelector ======================== #

# ======================== LazyMediaSelector ======================== #
@patch('src.section.FormatSection.inq_prompt')
@patch('src.section.FormatSection.get_lyd_media_autofill')
@patch('src.section.FormatSection.LazyMediaSelector._get_options')
def test_lazy_media_ask_media (get_options_mock:Mock, autofill_mock : Mock, prompt_mock:Mock):
  @dataclass
  class Case:
    options : list[str]
    prompt_ret : Union[str, None]
    do_prompt_called : bool
    autofill_ret : Union[int, None]
    do_autofill_called : bool
    expected_ret : str
    
  video = LazyMediaType.VIDEO.value
  audio = LazyMediaType.AUDIO.value
  
  case_ls : list[Case] = [
    # video and audio, select video
    Case(
      options=[video, audio],
      prompt_ret=video, do_prompt_called=True,
      autofill_ret=None, do_autofill_called=True,
      expected_ret=video
    ),
    # video and audio, select audio
    Case(
      options=[video, audio],
      prompt_ret=audio, do_prompt_called=True,
      autofill_ret=None, do_autofill_called=True,
      expected_ret=audio
    ),
    # video only
    Case(
      options=[video],
      prompt_ret=None, do_prompt_called=False,
      autofill_ret=None, do_autofill_called=False,
      expected_ret=video
    ),
    # audio only
    Case(
      options=[audio],
      prompt_ret=None, do_prompt_called=False,
      autofill_ret=None, do_autofill_called=False,
      expected_ret=audio
    ),
    # autofill
    Case(
      options=[video, audio],
      prompt_ret=None, do_prompt_called=False,
      autofill_ret=0, do_autofill_called=True,
      expected_ret=video
    )
  ]
  
  for case in case_ls:
    print('testing', case)
    get_options_mock.reset_mock()
    prompt_mock.reset_mock()
    autofill_mock.reset_mock()
    
    get_options_mock.return_value = case.options
    prompt_mock.return_value = { 'media_option': case.prompt_ret }
    autofill_mock.return_value = case.autofill_ret
    
    res = LazyMediaSelector()._ask_media([])
    
    assert res == case.expected_ret
    assert prompt_mock.called == case.do_prompt_called
    assert autofill_mock.called == case.do_autofill_called

def test_lazy_media_get_options ():
  fake_video_format = create_fake_format('v1')
  fake_audio_format = create_fake_format('a1')
  fake_both_format = create_fake_format('b1')
  
  fake_md1 = fake_videoMd(both_ls=[fake_both_format])
  fake_md2 = fake_videoMd(video_ls=[fake_video_format], audio_ls=[fake_audio_format])
  fake_md3 = fake_videoMd(video_ls=[fake_video_format])
  fake_md4 = fake_videoMd(audio_ls=[fake_audio_format])
  
  @dataclass
  class Case:
    md_ls : list[fake_videoMd]
    expected_ret : list[str]
    def __str__(self) -> str:
      return f'Case({self.md_ls}, {self.expected_ret})'
      
  case_ls : list[Case] = [
    Case([fake_md1], [LazyMediaType.VIDEO.value, LazyMediaType.AUDIO.value]),
    Case([fake_md2], [LazyMediaType.VIDEO.value, LazyMediaType.AUDIO.value]),
    Case([fake_md3], [LazyMediaType.VIDEO.value]),
    Case([fake_md4], [LazyMediaType.AUDIO.value])
  ]
  
  for case in case_ls:
    print('testing', case)
    assert LazyMediaSelector()._get_options(case.md_ls) == case.expected_ret
# ======================== LazyMediaSelector ======================== #