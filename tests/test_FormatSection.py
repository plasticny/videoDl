from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from typing import Union, Optional, Any
from dataclasses import dataclass
from uuid import uuid4
from random import choice

from src.section.FormatSection import FormatSection
from src.section.FormatSection import LazyFormatSection, LazyFormatSelector, LazyMediaSelector
from src.section.FormatSection import LazyFormatSectionRet
from src.service.MetaData import VideoMetaData
from src.structs.video_info import MediaType


# ======= helper ========= #
class fake_videoMd (VideoMetaData):
  def __init__(
    self,
    both_ls: list[Any] = [], video_ls: list[Any] = [], audio_ls: list[Any] = [],
    *args: ..., **kwargs: ...
  ):
    self._format = {
      'both': both_ls,
      'video': video_ls,
      'audio': audio_ls
    }
    
  @property
  def title (self) -> str:
    return ''
  @property
  def opts (Self) -> None:
    return None
  @property
  def url (self) -> str:
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

@patch('src.section.FormatSection.LazyFormatSection.check_format_str_available')
@patch('src.section.FormatSection.LazyFormatSection._sort_str')
@patch('src.section.FormatSection.LazyFormatSection._format_str')
@patch('src.section.FormatSection.LazyMediaSelector.ask_media')
@patch('src.section.FormatSection.LazyFormatSelector.ask_format_option')
def test_lazy_format_main(
  ask_format_mock: Mock, ask_media_mock: Mock,
  format_str_mock: Mock, sort_str_mock: Mock,
  check_format_str_mock: Mock
):
  @dataclass
  class Case:
    # mock
    format_available_seq: list[bool]
    # expected
    ask_format_called_cnt: int

  case_ls: list[Case] = [
    # format str available
    Case([True], 1),
    # format str not available once
    Case([False, True], 2),
  ]

  fake_md = fake_videoMd()

  for case in case_ls:
    format_str_ret = str(uuid4())
    sort_str_ret = str(uuid4())    
    media_ret: MediaType = choice(['Video', 'Audio'])
    
    ask_format_mock.reset_mock()
    ask_media_mock.reset_mock()
    format_str_mock.reset_mock()
    sort_str_mock.reset_mock()
    check_format_str_mock.reset_mock()

    ask_format_mock.return_value = LazyFormatSelector.SelectRes()
    ask_media_mock.return_value = media_ret
    format_str_mock.return_value = format_str_ret
    sort_str_mock.return_value = sort_str_ret
    check_format_str_mock.side_effect = case.format_available_seq

    ret: LazyFormatSectionRet = LazyFormatSection().run([fake_md])
    assert ret.media == media_ret
    assert ret.format_ls == [format_str_ret]
    assert ret.sort_ls == [sort_str_ret]
    assert ask_format_mock.call_count == case.ask_format_called_cnt

def test_lazy_format_format_str ():
  @dataclass
  class Case:
    meida: MediaType
    format_option_win: bool
    expected_ret: str

  WIN_VCODEC_REGEX_FILTER = "[vcodec~='^(?!.*(hev|av01)).*$']"
  WIN_ACODEC_REGEX_FILTER = "[acodec~='^(?!.*opus).*$']"

  case_ls: list[Case] = [
    Case('Video', False, "bv*+ba/b"),
    Case('Video', True, f'bv*{WIN_VCODEC_REGEX_FILTER}+ba{WIN_ACODEC_REGEX_FILTER}/b{WIN_VCODEC_REGEX_FILTER}{WIN_ACODEC_REGEX_FILTER}'),
    Case('Audio', False, f'ba/b'),
    Case('Audio', True, f'ba{WIN_ACODEC_REGEX_FILTER}/b{WIN_ACODEC_REGEX_FILTER}')
  ]

  for case in case_ls:
    format_option = LazyFormatSelector.SelectRes(WIN=case.format_option_win)
    assert LazyFormatSection()._format_str(case.meida, format_option) == case.expected_ret # type: ignore

def test_lazy_format_sort_str ():
  @dataclass
  class Case:
    media: MediaType
    format_option_hrls: bool
    expected_ret: Optional[str]

  case_ls: list[Case] = [
    Case('Video', False, None),
    Case('Video', True, 'res,+size'),
    Case('Audio', False, None),
    Case('Audio', True, 'asr,+size')
  ]

  for case in case_ls:
    format_option = LazyFormatSelector.SelectRes(HRLS=case.format_option_hrls)
    assert LazyFormatSection()._sort_str(case.media, format_option) == case.expected_ret # type: ignore

@patch('src.section.FormatSection.DownloadOpt')
@patch('src.section.FormatSection.Ytdlp')
def test_lazy_format_check_format_str_available (
  ytdlp_mock: Mock, download_opt_mock: Mock
):
  class fakeDownloadOpt:
    def __init__ (self, *args: ...):
      pass
    def set_format (self, *args: ...):
      pass
    @staticmethod
    def to_ytdlp_dl_opt (*args: ...):
      pass

  check_format_available_mock = Mock()

  class fakeYtdlp:
    def __init__ (self, *args: ...):
      print('fakeYtdlp init')
      pass
    def check_format_available (self, *args: ...):
      return check_format_available_mock()
    
  ytdlp_mock.side_effect = fakeYtdlp
  download_opt_mock.side_effect = fakeDownloadOpt

  @dataclass
  class Case:
    format_option_win: bool
    ytdlp_ret: bool
    expected_ret: bool

  case_ls: list[Case] = [
    Case(False, True, True),
    Case(False, False, True),
    Case(True, True, True),
    Case(True, False, False)
  ]

  for case in case_ls:
    print('testing', case)
    
    check_format_available_mock.return_value = case.ytdlp_ret
    format_option = LazyFormatSelector.SelectRes(WIN=case.format_option_win)

    ret = LazyFormatSection().check_format_str_available(
      fake_videoMd(), '', format_option
    )
    assert ret == case.expected_ret

# ======================== LazyFormatSelector ======================== #
@patch('src.section.FormatSection.inq_prompt')
@patch('src.service.autofill.get_lyd_format_option_autofill')
@patch('src.section.FormatSection.LazyFormatSelector._get_options')
def test_lazy_format_ask_format(
  get_options_mock: Mock, autofill_mock: Mock, prompt_mock: Mock
):
  """
  This testing will not test the autofill and the prompt
  """
  @dataclass
  class Case:
    # mock return
    has_any_option: bool
    prompt: dict[str, list[LazyFormatSelector.Option]]
    # expected
    expected_ret: LazyFormatSelector.SelectRes
    prompt_called: bool

  option_hrls = LazyFormatSelector.OPTIONS['HRLS']
  option_win = LazyFormatSelector.OPTIONS['WIN']

  case_ls: list[Case] = [
    # no options
    Case(
      has_any_option=False, prompt={},
      expected_ret=LazyFormatSelector.SelectRes(), prompt_called=False
    ),
    # has option 1
    Case(
      has_any_option=True, prompt={ 'format_option': [] },
      expected_ret=LazyFormatSelector.SelectRes(HRLS=False, WIN=False), prompt_called=True
    ),
    # has option 2
    Case(
      has_any_option=True, prompt={ 'format_option': [option_hrls] },
      expected_ret=LazyFormatSelector.SelectRes(HRLS=True, WIN=False), prompt_called=True
    ),
    # has option 3
    Case(
      has_any_option=True, prompt={ 'format_option': [option_win] },
      expected_ret=LazyFormatSelector.SelectRes(HRLS=False, WIN=True), prompt_called=True
    )
  ]

  for case in case_ls:
    get_options_mock.reset_mock()
    autofill_mock.reset_mock()
    prompt_mock.reset_mock()

    get_options_mock.return_value = [option_hrls, option_win] if case.has_any_option else []
    autofill_mock.return_value = None
    prompt_mock.return_value = case.prompt

    ret = LazyFormatSelector().ask_format_option([], 'Video', None)

    assert ret == case.expected_ret
    assert prompt_mock.called == case.prompt_called

def test_lazy_format_get_options ():
  @dataclass
  class Case:
    # input
    media: MediaType
    # expected
    expected_ret_empty: bool

  case_ls: list[Case] = [
    Case('Video', False),
    Case('Audio', True)
  ]

  for case in case_ls:
    ret = LazyFormatSelector()._get_options([], case.media) # type: ignore
    assert (len(ret) == 0) == case.expected_ret_empty
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
    
  video: MediaType = 'Video'
  audio: MediaType = 'Audio'
  
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
    
    res = LazyMediaSelector().ask_media([])
    
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
    expected_ret : list[MediaType]
    def __str__(self) -> str:
      return f'Case({self.md_ls}, {self.expected_ret})'
      
  case_ls : list[Case] = [
    Case([fake_md1], ['Video', 'Audio']),
    Case([fake_md2], ['Video', 'Audio']),
    Case([fake_md3], ['Video']),
    Case([fake_md4], ['Audio'])
  ]
  
  for case in case_ls:
    print('testing', case)
    assert LazyMediaSelector()._get_options(case.md_ls) == case.expected_ret
# ======================== LazyMediaSelector ======================== #