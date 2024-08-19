from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from typing_extensions import Union, Optional, TypedDict
from dataclasses import dataclass
from pytest import raises as assert_raises

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

@patch('src.section.FormatSection.LazyFormatSection._best_audio')
@patch('src.section.FormatSection.LazyFormatSection._select_video_format')
@patch('src.section.FormatSection.LazyMediaSelector._ask_media')
@patch('src.section.FormatSection.LazyFormatSelector._ask_format_option')
def test_lazy_format_main(
    ask_format_mock: Mock, ask_media_mock: Mock,
    select_video_format_mock: Mock, best_audio_mock: Mock
  ):
  @dataclass
  class Case:
    md_ls : list[VideoMetaData]
    media : str
    audio_format: Optional[str]
    video_format: Optional[str]
    expected_media_ret: str
    expected_format_ret: Union[str, BundledFormat, None]
    expected_err_raised: Optional[Exception] = None
  
  select_video_format_ret = 'v1'
  best_audio_ret = 'a1'
  
  fake_md = fake_videoMd()
  video = LazyMediaType.VIDEO.value
  audio = LazyMediaType.AUDIO.value
  
  case_ls : list[Case] = [
    # video
    # normal case
    Case(
      md_ls=[fake_md], media=video,
      audio_format=best_audio_ret, video_format=select_video_format_ret,
      expected_media_ret=video,
      expected_format_ret=BundledFormat(select_video_format_ret, best_audio_ret)
    ),
    # no video
    Case(
      md_ls=[fake_md], media=video,
      audio_format=None, video_format=None,
      expected_media_ret=video, expected_format_ret=None,
      expected_err_raised=ValueError
    ),
    # audio
    # normal case
    Case(
      md_ls=[fake_md], media=audio,
      audio_format=best_audio_ret, video_format=None,
      expected_media_ret=audio, expected_format_ret=best_audio_ret
    ),
    # no audio
    Case(
      md_ls=[fake_md], media=audio,
      audio_format=None, video_format=None,
      expected_media_ret=audio, expected_format_ret=None,
      expected_err_raised=ValueError
    )
  ]
  
  for case in case_ls:
    print('testing', case)
    
    ask_format_mock.reset_mock()
    ask_media_mock.reset_mock()
    ask_format_mock.return_value = LazyFormatSelector.SelectRes()
    ask_media_mock.return_value = case.media

    select_video_format_mock.return_value = case.video_format
    best_audio_mock.return_value = case.audio_format

    # if the case expected error raised
    if case.expected_err_raised is not None:
      with assert_raises(case.expected_err_raised):
        LazyFormatSection().run(case.md_ls)
      continue

    # if the case expected no error
    ret : LazyFormatSectionRet = LazyFormatSection().run(case.md_ls)
    assert ret.media == case.expected_media_ret
    assert ret.format_ls == [case.expected_format_ret]

def test_lazy_format_best_audio ():
  @dataclass
  class FileFormat:
    codec: str
    format_id: str
    def to_both_dict (self):
      return { 'audio': self.__dict__ }

  @dataclass
  class Case:
    format_option: LazyFormatSelector.SelectRes
    audio_formats: list[FileFormat]
    both_formats: list[FileFormat]
    expectret_ret: Union[str, None]

  a1 = FileFormat('opus', 'a1')
  a2 = FileFormat('aac', 'a2')

  case_ls: list[Case] = [
    # the format in audio formats
    Case(
      format_option=LazyFormatSelector.SelectRes(WIN=False),
      audio_formats=[a1], both_formats=[],
      expectret_ret=a1.format_id
    ),
    # the format in both formats
    Case(
      format_option=LazyFormatSelector.SelectRes(WIN=False),
      audio_formats=[], both_formats=[a1],
      expectret_ret=a1.format_id
    ),
    # win, the format in both formats
    Case(
      format_option=LazyFormatSelector.SelectRes(WIN=True),
      audio_formats=[a1], both_formats=[a2],
      expectret_ret=a2.format_id
    ),
    # no available format
    Case(
      format_option=LazyFormatSelector.SelectRes(WIN=True),
      audio_formats=[a1], both_formats=[a1],
      expectret_ret=None
    )
  ]

  for case in case_ls:
    audio_ls = [f.__dict__ for f in case.audio_formats]
    both_ls = [f.to_both_dict() for f in case.both_formats]
    md = fake_videoMd(audio_ls=audio_ls, both_ls=both_ls)

    ret = LazyFormatSection()._best_audio(md, case.format_option)
    assert ret == case.expectret_ret

def test_lazy_format_select_video_format ():
  @dataclass
  class FileFormat:
    format_id: str
    codec: str
    width: int
    height: int

  @dataclass
  class Case:
    format_option: LazyFormatSelector.SelectRes
    video_formats: list[FileFormat]
    expectret_ret: Union[str, None]

  v1 = FileFormat('v1', 'avc', 1920, 1080)
  v2 = FileFormat('v2', 'avc', 1920, 1080)
  v3 = FileFormat('v3', 'hev', 1920, 1080)
  v4 = FileFormat('v4', 'av01', 1920, 1080)
  v5 = FileFormat('v5', 'avc', 720, 480)

  case_ls: list[Case] = [
    # normal case
    Case(
      format_option=LazyFormatSelector.SelectRes(),
      video_formats=[v1, v2, v3],
      expectret_ret=v1.format_id
    ),
    # hrls
    Case(
      format_option=LazyFormatSelector.SelectRes(HRLS=True),
      video_formats=[v1, v2, v3, v5],
      expectret_ret=v3.format_id
    ),
    # win
    Case(
      format_option=LazyFormatSelector.SelectRes(WIN=True),
      video_formats=[v3, v4, v1],
      expectret_ret=v1.format_id
    ),
    # hrls + win
    Case(
      format_option=LazyFormatSelector.SelectRes(HRLS=True, WIN=True),
      video_formats=[v1, v3, v4, v2, v5],
      expectret_ret=v2.format_id
    ),
    # no available format
    Case(
      format_option=LazyFormatSelector.SelectRes(WIN=True),
      video_formats=[v3, v4],
      expectret_ret=None
    )
  ]

  for case in case_ls:
    video_ls = [f.__dict__ for f in case.video_formats]
    md = fake_videoMd(video_ls=video_ls)
    ret = LazyFormatSection()._select_video_format(md, case.format_option)
    assert ret == case.expectret_ret
  
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