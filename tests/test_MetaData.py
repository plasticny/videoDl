from unittest.mock import patch, Mock
from pytest import raises

from json import loads as jsonLoads
from typing import Literal, Union, TypedDict, Optional, Type
from dataclasses import dataclass
from uuid import uuid4

from src.service.MetaData import fetchMetaData, MetaDataOpt
from src.service.MetaData import MetaData
from src.service.MetaData import VideoMetaData, BiliBiliVideoMetaData, FacebookVideoMetaData
from src.service.MetaData import PlaylistMetaData, BiliBiliPlaylistMetaData
from src.service.MetaData import TMdFormats
from src.service.urlHelper import UrlSource

from src.structs.video_info import Subtitle

@patch('src.service.MetaData.FacebookVideoMetaData')
@patch('src.service.MetaData.BiliBiliPlaylistMetaData')
@patch('src.service.MetaData.BiliBiliVideoMetaData')
@patch('src.service.MetaData.PlaylistMetaData')
@patch('src.service.MetaData.VideoMetaData')
@patch('src.service.MetaData.getSource')
@patch('src.service.MetaData.ytdlp_extract_metadata')
def test_fetchMetaData_type(
  extract_metadata_mock:Mock, getSource_mock:Mock,
  video_md_mock:Mock, playlist_md_mock:Mock,
  bili_video_md_mock:Mock, bili_playlist_md_mock:Mock,
  fb_video_md_mock:Mock
):
  """ Test the type of metadata returned by fetchMetaData """
  class fake_video_md (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  class fake_bili_video_md (BiliBiliVideoMetaData):
    def __init__(self, *args, **kwargs):
      pass
  class fake_facebook_video_md (FacebookVideoMetaData):
    def __init__(self, *args, **kwargs):
      pass
  class fake_playlist_md (PlaylistMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  class fake_bili_playlist_md (BiliBiliPlaylistMetaData):
    def __init__(self, *args, **kwargs):
      pass

  video_md_mock.return_value = fake_video_md()
  bili_video_md_mock.return_value = fake_bili_video_md()
  fb_video_md_mock.return_value = fake_facebook_video_md()
  playlist_md_mock.return_value = fake_playlist_md()
  bili_playlist_md_mock.return_value = fake_bili_playlist_md()

  @dataclass
  class Case:
    md_type : Literal['video', 'playlist']
    do_error : bool
    source : Union[str, UrlSource]
    expected : Optional[Type[MetaData]]
    
  case_ls : list[Case] = [
    Case('video', False, 'fake source', fake_video_md),
    Case('video', False, UrlSource.BILIBILI, fake_bili_video_md),
    Case('video', False, UrlSource.FACEBOOK, fake_facebook_video_md),
    Case('video', False, UrlSource.IG, fake_video_md),
    Case('playlist', False, 'fake source', fake_playlist_md),
    Case('playlist', False, UrlSource.BILIBILI, fake_bili_playlist_md),
    Case('video', True, 'fake source', None)
  ]
  
  for idx, case in enumerate(case_ls):
    print('testing case', idx + 1)
    
    extract_metadata_mock.reset_mock()
    getSource_mock.reset_mock()
    
    if case.do_error:
      extract_metadata_mock.side_effect = Exception('error')
    else:
      extract_metadata_mock.return_value = { '_type': case.md_type }
    getSource_mock.return_value = case.source
    
    opt = MetaDataOpt()
    opt.url = 'fake url'

    if case.do_error:
      with raises(Exception):
        md = fetchMetaData(opt)
        assert md is None
    else:
      md = fetchMetaData(opt)
      assert case.expected is not None and isinstance(md, case.expected)

def test_videoMd_getSubtitles():
  """test getSubtitles method of VideoMetaData"""
  class fake_video_md (VideoMetaData):
    def __init__ (self, metadata, *args, **kwargs):
      self.metadata = metadata
  
  subtitle_md = {
    'en': [
      {'url': 'fake url', 'name': 'English'},
    ],
    'zh': [
      {'url': 'fake url'}, 
      {'url': 'fake url', 'name': 'Chinese'}
    ]
  }
  auto_subtitle_md = {
    'auto-en': [
      {'url': 'fake url', 'name': 'Auto English'},
    ],
    'auto-zh': [
      {'url': 'fake url'}, 
      {'url': 'fake url', 'name': 'Auto Chinese'}
    ]
  }
  expected_sub = [
    Subtitle('en', 'English'),
    Subtitle('zh', 'Chinese')
  ]
  expected_auto_sub = [
    Subtitle('auto-en', 'Auto English', True),
    Subtitle('auto-zh', 'Auto Chinese', True)
  ]

  # test cases [(subtitle metadata, auto subtitle metadata, expected subtitle, expected auto subtitle)]
  case_ls : list[tuple[dict, dict, list[Subtitle], list[Subtitle]]] = [
    # only subtitle
    (subtitle_md, {}, expected_sub, []),
    # subtitle and auto subtitle
    (subtitle_md, auto_subtitle_md, expected_sub, expected_auto_sub),
    # no subtitle key in metadata
    ({}, {}, [], [])
  ]

  for case in case_ls:
    print('testing', case)
    case_subtitle_md, case_auto_subtitle_md, case_expected_sub, case_expected_auto_sub = case
    
    sub, auto_sub = fake_video_md({
      'subtitles': case_subtitle_md,
      'automatic_captions': case_auto_subtitle_md
    })._getSubtitles()
    assert sub == case_expected_sub
    assert auto_sub == case_expected_auto_sub

def test_videoMd_extract_format():
  class fake_video_md (VideoMetaData):
    def __init__ (self, metadata, *args, **kwargs):
      self.metadata = metadata
  
  fake_metadata = {'formats': [
    { 'format_id': 0 }, # some format without audio or video
    # m4a audio and mp4 video
    { 'tbr': 1, 'format_id': '1', 'acodec': 'm4a', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'm4a', 'video_ext': 'mp4', 'resolution': '720x720' },
    # no audio and avi video
    { 'tbr': 3, 'format_id': '2', 'acodec': 'none', 'vcodec': 'avi', 'ext': 'avi', 'audio_ext': 'none', 'video_ext': 'avi', 'resolution': '720x720' },
    # mp3 audio and no video
    { 'tbr': 4, 'format_id': '3', 'acodec': 'mp3', 'vcodec': 'none', 'ext': 'mp3', 'audio_ext': 'mp3', 'video_ext': 'none' },
    # no audio and mp4 video
    { 'tbr': 2, 'format_id': '4', 'acodec': 'none', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'none', 'video_ext': 'mp4', 'resolution': '720x720' },
    # no audio and mp4 video
    { 'tbr': 5, 'format_id': '5', 'acodec': 'none', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'none', 'video_ext': 'mp4', 'resolution': '360x360' },
    # mp4 audio
    { 'tbr': 4, 'format_id': '6', 'format_note': 'Audio', 'vcodec': 'none', 'audio_ext': 'mp4', 'video_ext': 'none' },
  ]}
  
  expected_result : TMdFormats = {
    'both': [
      {
        'tbr': 1, 'format_id': '1',
        'audio': { 'tbr': 1, 'format_id': '1', 'codec': 'm4a', 'ext': 'm4a' },
        'video': { 'tbr': 1, 'format_id': '1', 'codec': 'mp4', 'ext': 'mp4', 'height': 720, 'width': 720 }
      }
    ],
    'audio': [
      { 'tbr': 4, 'format_id': '3', 'codec': 'mp3', 'ext': 'mp3' },
      { 'tbr': 4, 'format_id': '6', 'codec': 'none', 'ext': 'mp4' }
    ],
    'video': [
      { 'tbr': 3, 'format_id': '2', 'codec': 'avi', 'ext': 'avi', 'height': 720, 'width': 720 },
      { 'tbr': 2, 'format_id': '4', 'codec': 'mp4', 'ext': 'mp4', 'height': 720, 'width': 720 },
      { 'tbr': 1, 'format_id': '1', 'codec': 'mp4', 'ext': 'mp4', 'height': 720, 'width': 720 },
      { 'tbr': 5, 'format_id': '5', 'codec': 'mp4', 'ext': 'mp4', 'height': 360, 'width': 360 }
    ]
  }
  
  assert fake_video_md(fake_metadata)._extract_format() == expected_result

@patch('src.service.MetaData.VideoMetaData._extract_format')
def test_fb_videoMd_extract_format (video_md_extract_format_mock:Mock):
  class fake_fb_video_md (FacebookVideoMetaData):
    def __init__ (self, formats, *args, **kwargs):
      self.metadata = { 'formats': formats }
  
  sd_format = { 'format_id': 'sd' }
  hd_format = { 'format_id': 'hd' }
  other_format = { 'format_id': 'other' }
    
  # test cases [(format metadata, expected formats of both)]
  case_ls : list[tuple[dict, list[dict]]] = [
    (hd_format, [hd_format]),
    (sd_format, [sd_format]),
    (other_format, [])
  ]
  
  for case in case_ls:
    print('testing', case)
    case_format, case_expected_both = case

    video_md_extract_format_mock.return_value = {
      'video': [], 'audio': [], 'both': []
    }
    
    formats = fake_fb_video_md([case_format])._extract_format()
    
    assert len(formats['both']) == len(case_expected_both)
    for ret_format, expected_format in zip(formats['both'], case_expected_both):
      assert ret_format['format_id'] == expected_format['format_id']
  
@patch('src.service.MetaData.getSource')
def test_MetadataOpt_to_ytdlp_opt(get_source_mock:Mock):
  """
    Check important options are contained in the returned dict
  """
  # not bilibili
  opt = MetaDataOpt()
  opt.url = 'url'
  opt.cookie_file_path = 'cookie'
  opt.login_browser = 'browser'
  
  ret_opt = MetaDataOpt.to_ytdlp_opt(opt)
  assert ret_opt['extract_flat']
  assert ret_opt['listsubtitles']
  
  # bilibili (not list subtitle)
  get_source_mock.return_value = UrlSource.BILIBILI
  assert MetaDataOpt.to_ytdlp_opt(opt)['listsubtitles'] == False

def test_fetch_yt_video_ng_():
  """
  test fetch metadata of a real youtube video with url
  this test might failed if there are changes in the video
  """
  opt = MetaDataOpt()
  opt.url = 'https://www.youtube.com/watch?v=zKAxWU4odvE'
  md = fetchMetaData(opt)
  
  with open('tests/testFiles/test_MetaData/yt_v.json', 'r', encoding='utf-8') as f:
    expected = jsonLoads(f.read())

  assert isinstance(md, VideoMetaData)
  assert md.title == expected['title']
  assert md.url == expected['original_url']
  assert len(md.subtitles) == len(expected['subtitles'])

def test_fetch_bili_ls_ng_():
  """test fetch metadata of a real bilibili playlist with config object"""
  url = 'https://www.bilibili.com/video/BV1bN411s7VT'
  opt = MetaDataOpt()
  opt.url = url

  md = fetchMetaData(opt)
  with open('tests/testFiles/test_MetaData/bili_ls.json', 'r') as f:
    expected = jsonLoads(f.read())

  assert md.isPlaylist()
  assert md.title == expected['title']
  assert md.url == expected['original_url']
  assert md.id == expected['id']

  # test playlist items
  assert md.playlist_count == expected['playlist_count']
  assert len(md.videos) == expected['playlist_count']
  for idx, v in enumerate(md.videos):
    assert isinstance(v, VideoMetaData)
    assert v.title == expected['entries'][idx]['title']

@patch('src.service.MetaData.fetchMetaData')
def test_fetch_playlist_videos (fetch_md_mock : Mock):
  """ test fetchVideoMd of PlaylistMetaData class """
  class fake_Entry (TypedDict):
    url : str
  
  class fake_MetaDataOpt (MetaDataOpt):
    def __init__(self) -> None:
      self.url = None
    def copy (self):
      return fake_MetaDataOpt()
    
  class fake_VideoMetaData (VideoMetaData):
    def __init__(self):
      pass
    def isPlaylist (self) -> bool:
      return False
  
  @dataclass
  class Case:
    entry_ls : list[fake_Entry]
    fetch_res_ls : list[Union[VideoMetaData, None]]
    expected : list[VideoMetaData]
    @property
    def metadata (self) -> dict:
      return {
        'entries': self.entry_ls,
        'playlist_count': len(self.entry_ls)
      }
  
  fake_entry1 = fake_Entry(url=uuid4().__str__())
  fake_entry2 = fake_Entry(url=uuid4().__str__())
  
  fake_video_md1 = fake_VideoMetaData()
  fake_video_md2 = fake_VideoMetaData()
  
  case_ls : list[Case] = [
    Case(
      entry_ls=[fake_entry1, fake_entry1, fake_entry2],
      fetch_res_ls = [fake_video_md1, None, fake_video_md2],
      expected=[fake_video_md1, fake_video_md2]
    )
  ]
  
  for idx, case in enumerate(case_ls):
    print('testing case', idx + 1)
    
    fetch_md_mock.reset_mock()
    fetch_md_mock.side_effect = case.fetch_res_ls
    
    # fetchVideoMd is called in the constructor
    md = PlaylistMetaData(case.metadata, fake_MetaDataOpt())
    
    assert fetch_md_mock.call_count == len(case.entry_ls)
    for call, entry in zip(fetch_md_mock.call_args_list, case.entry_ls):
      assert call[0][0].url == entry['url']
      
    assert len(md.videos) == len(case.expected)
    for actual, expected in zip(md.videos, case.expected):
      assert actual == expected
    