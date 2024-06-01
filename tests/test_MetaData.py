from unittest.mock import patch, Mock

from json import loads as jsonLoads
from typing import Literal

from src.service.MetaData import fetchMetaData, MetaDataOpt
from src.service.MetaData import VideoMetaData, BiliBiliVideoMetaData, FacebookVideoMetaData, IGVideoMetaData
from src.service.MetaData import PlaylistMetaData, BiliBiliPlaylistMetaData
from src.service.MetaData import TMdFormats
from src.service.urlHelper import UrlSource

from src.structs.video_info import Subtitle

@patch('src.service.MetaData.IGVideoMetaData')
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
  fb_video_md_mock:Mock, ig_video_md_mock:Mock
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
  class fake_ig_video_md (IGVideoMetaData):
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
  ig_video_md_mock.return_value = fake_ig_video_md()
  playlist_md_mock.return_value = fake_playlist_md()
  bili_playlist_md_mock.return_value = fake_bili_playlist_md()

  # test cases [(extract metadata returned type, url source, expected metadata type)]
  case_ls : list[tuple[Literal['video', 'playlist'], str, type]] = [
    ('video', 'fake source', VideoMetaData),
    ('video', UrlSource.BILIBILI, BiliBiliVideoMetaData),
    ('video', UrlSource.FACEBOOK, FacebookVideoMetaData),
    ('video', UrlSource.IG, IGVideoMetaData),
    ('playlist', 'fake source', PlaylistMetaData),
    ('playlist', UrlSource.BILIBILI, BiliBiliPlaylistMetaData)  
  ]
  
  for case in case_ls:
    print('testing', case)
    case_metadata_type, case_source, case_expected_ret_type = case
    
    extract_metadata_mock.reset_mock()
    getSource_mock.reset_mock()
    
    extract_metadata_mock.return_value = { '_type': case_metadata_type }
    getSource_mock.return_value = case_source
    assert isinstance(fetchMetaData(MetaDataOpt()), case_expected_ret_type)

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
    {}, # some format without audio or video
    { 'tbr': 1, 'format_id': '1', 'acodec': 'm4a', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'm4a', 'video_ext': 'mp4', 'resolution': '720x720' },
    { 'tbr': 3, 'format_id': '2', 'acodec': 'none', 'vcodec': 'avi', 'ext': 'avi', 'audio_ext': 'none', 'video_ext': 'avi', 'resolution': '720x720' },
    { 'tbr': 4, 'format_id': '3', 'acodec': 'mp3', 'vcodec': 'none', 'ext': 'mp3', 'audio_ext': 'mp3', 'video_ext': 'none' },
    { 'tbr': 2, 'format_id': '4', 'acodec': 'none', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'none', 'video_ext': 'mp4', 'resolution': '720x720' }
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
      { 'tbr': 1, 'format_id': '1', 'codec': 'm4a', 'ext': 'm4a' }
    ],
    'video': [
      { 'tbr': 2, 'format_id': '4', 'codec': 'mp4', 'ext': 'mp4', 'height': 720, 'width': 720 },
      { 'tbr': 1, 'format_id': '1', 'codec': 'mp4', 'ext': 'mp4', 'height': 720, 'width': 720 }
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
  
def test_ig_videoMd_extract_format ():
  class fake_ig_video_md (IGVideoMetaData):
    def __init__ (self, formats, *args, **kwargs):
      self.metadata = { 'formats': formats }
  
  f1 = { 'format_id': '1', 'height': 720, 'width': 720 }
  f2 = { 'format_id': '2', 'height': 1280, 'width': 1280 }
  
  # hd
  formats = fake_ig_video_md([f1, f2])._extract_format()
  assert len(formats['both']) == 2
  assert formats['both'][0]['format_id'] == '2'
  assert formats['both'][1]['format_id'] == '1'

@patch('src.service.MetaData.getSource')
def test_MetadataOpt_to_ytdlp_opt(get_source_mock:Mock):
  """
    Check important options are contained in the returned dict
  """
  # not bilibili
  opt = MetaDataOpt()
  opt.url = 'url'
  
  ret_opt = MetaDataOpt.to_ytdlp_opt(opt)
  assert ret_opt['extract_flat']
  assert ret_opt['listsubtitles']
  
  # bilibili (not list subtitle)
  get_source_mock.return_value = UrlSource.BILIBILI
  assert MetaDataOpt.to_ytdlp_opt(opt)['listsubtitles'] == False

def test_fetch_yt_video():
  """test fetch metadata of a real youtube video with url"""
  opt = MetaDataOpt()
  opt.url = 'https://www.youtube.com/watch?v=zKAxWU4odvE'
  md = fetchMetaData(opt)
  
  with open('tests/testFiles/test_MetaData/yt_v.json', 'r', encoding='utf-8') as f:
    expected = jsonLoads(f.read())

  assert isinstance(md, VideoMetaData)
  assert md.title == expected['title']
  assert md.url == expected['original_url']
  
  assert len(md.subtitles) == len(expected['subtitles'])
  assert len(md.autoSubtitles) == len(expected['automatic_captions'])

def test_fetch_bili_ls():
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
