from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from typing_extensions import Union, Optional, TypedDict
from dataclasses import dataclass
from pytest import raises as assert_raises
from uuid import uuid4
from random import choice

from src.section.FormatSection import FormatSection
from src.section.FormatSection import LazyFormatSection, LazyFormatSelector, LazyMediaSelector
from src.section.FormatSection import LazyMediaType, LazyFormatSectionRet
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

@patch('src.section.FormatSection.LazyFormatSection._sort_str')
@patch('src.section.FormatSection.LazyFormatSection._format_str')
@patch('src.section.FormatSection.LazyMediaSelector._ask_media')
@patch('src.section.FormatSection.LazyFormatSelector._ask_format_option')
def test_lazy_format_main(
    ask_format_mock: Mock, ask_media_mock: Mock,
    format_str_mock: Mock, sort_str_mock: Mock
  ):
  format_str_ret = str(uuid4())
  sort_str_ret = str(uuid4())
  
  fake_md = fake_videoMd()
  media_ret = choice([LazyMediaType.VIDEO.value, LazyMediaType.AUDIO.value])
  
  ask_format_mock.return_value = LazyFormatSelector.SelectRes()
  ask_media_mock.return_value = media_ret
  format_str_mock.return_value = format_str_ret
  sort_str_mock.return_value = sort_str_ret

  ret: LazyFormatSectionRet = LazyFormatSection().run([fake_md])
  assert ret.media == media_ret
  assert ret.format_ls == [format_str_ret]
  assert ret.sort_ls == [sort_str_ret]

def test_lazy_format_format_str ():
  @dataclass
  class Case:
    meida: str
    format_option_win: bool
    expected_ret: str

  video = LazyMediaType.VIDEO.value
  audio = LazyMediaType.AUDIO.value

  WIN_VCODEC_REGEX_FILTER = "[vcodec~='^(?!.*(hev|av01)).*$']"
  WIN_ACODEC_REGEX_FILTER = "[acodec~='^(?!.*opus).*$']"

  case_ls: list[Case] = [
    Case(video, False, "bv*+ba/b"),
    Case(video, True, f'bv*{WIN_VCODEC_REGEX_FILTER}+ba{WIN_ACODEC_REGEX_FILTER}/b{WIN_VCODEC_REGEX_FILTER}{WIN_ACODEC_REGEX_FILTER}'),
    Case(audio, False, f'ba/b'),
    Case(audio, True, f'ba{WIN_ACODEC_REGEX_FILTER}/b{WIN_ACODEC_REGEX_FILTER}')
  ]

  for case in case_ls:
    format_option = LazyFormatSelector.SelectRes(WIN=case.format_option_win)
    assert LazyFormatSection()._format_str(case.meida, format_option) == case.expected_ret

def test_lazy_format_sort_str ():
  @dataclass
  class Case:
    media: str
    format_option_hrls: bool
    expected_ret: Optional[str]

  case_ls: list[Case] = [
    Case(LazyMediaType.VIDEO.value, False, None),
    Case(LazyMediaType.VIDEO.value, True, 'res,+size'),
    Case(LazyMediaType.AUDIO.value, False, None),
    Case(LazyMediaType.AUDIO.value, True, 'asr,+size')
  ]

  for case in case_ls:
    format_option = LazyFormatSelector.SelectRes(HRLS=case.format_option_hrls)
    assert LazyFormatSection()._sort_str(case.media, format_option) == case.expected_ret

# ======================== LazyFormatSelector ======================== #
@patch('src.section.FormatSection.inq_prompt')
@patch('src.section.FormatSection.LazyFormatSelector._get_options')
def test_lazy_format_ask_format(get_options_mock:Mock, prompt_mock:Mock):
  """
  This testing will not test the autofill and the prompt
  """
  @dataclass
  class Case:
    media: LazyMediaType
    option_exists: bool
    prompt_called: bool

  video = LazyMediaType.VIDEO.value
  audio = LazyMediaType.AUDIO.value

  case_ls: list[Case] = [
    # audio
    Case(media=audio, option_exists=True, prompt_called=False),
    # option exists
    Case(media=video, option_exists=True, prompt_called=True),
    # option not exists
    Case(media=video, option_exists=False, prompt_called=False)
  ]
  
  for case in case_ls:
    print('testing', case)
    
    get_options_mock.reset_mock()
    prompt_mock.reset_mock()
    
    fake_options = []
    if case.option_exists:
      fake_options.append('fake_option')
    get_options_mock.return_value = fake_options
    
    LazyFormatSelector()._ask_format_option([], case.media)
    assert prompt_mock.called == case.prompt_called

def test_lazy_format_get_options ():
  # currently no test needed
  pass
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