from unittest.mock import patch, Mock

from json import loads as jsonLoads

from src.service.MetaData import fetchMetaData, PlaylistMetaData, VideoMetaData, MetaDataOpt
from src.service.MetaData import BiliBiliPlaylistMetaData, BiliBiliVideoMetaData
from src.service.MetaData import TMdFormats
from src.service.urlHelper import UrlSource

from src.structs.video_info import Subtitle

@patch('src.service.MetaData.BiliBiliPlaylistMetaData')
@patch('src.service.MetaData.BiliBiliVideoMetaData')
@patch('src.service.MetaData.PlaylistMetaData')
@patch('src.service.MetaData.VideoMetaData')
@patch('src.service.MetaData.getSource')
@patch('src.service.MetaData.ytdlp_extract_metadata')
def test_fetchMetaData_type(
  extract_metadata_mock:Mock, getSource_mock:Mock,
  video_md_mock:Mock, playlist_md_mock:Mock,
  bili_video_md_mock:Mock, bili_playlist_md_mock:Mock
):
  """ Test the type of metadata returned by fetchMetaData """
  class fake_video_md (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  class fake_bili_video_md (BiliBiliVideoMetaData):
    def __init__(self, *args, **kwargs):
      pass
  class fake_playlist_md (PlaylistMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  class fake_bili_playlist_md (BiliBiliPlaylistMetaData):
    def __init__(self, *args, **kwargs):
      pass

  video_md_mock.return_value = fake_video_md()
  playlist_md_mock.return_value = fake_playlist_md()
  bili_video_md_mock.return_value = fake_bili_video_md()
  bili_playlist_md_mock.return_value = fake_bili_playlist_md()

  # == test video == #
  extract_metadata_mock.return_value = { '_type': 'video' }
  getSource_mock.return_value = 'fake source'
  assert isinstance(fetchMetaData(MetaDataOpt()), VideoMetaData)
  
  getSource_mock.return_value = UrlSource.BILIBILI
  assert isinstance(fetchMetaData(MetaDataOpt()), BiliBiliVideoMetaData)

  # === test playlist === #
  extract_metadata_mock.return_value = { '_type': 'playlist' }
  getSource_mock.return_value = 'fake source'
  assert isinstance(fetchMetaData(MetaDataOpt()), PlaylistMetaData)
  
  getSource_mock.return_value = UrlSource.BILIBILI
  assert isinstance(fetchMetaData(MetaDataOpt()), BiliBiliPlaylistMetaData)

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

  # test only subtitle
  sub, auto_sub = fake_video_md({'subtitles': subtitle_md})._getSubtitles()
  assert sub == expected_sub
  assert auto_sub == []

  # test subtitle and auto subtitle
  sub, auto_sub = fake_video_md({
    'subtitles': subtitle_md, 
    'automatic_captions': auto_subtitle_md
  })._getSubtitles()
  assert sub == expected_sub
  assert auto_sub == expected_auto_sub

def test_videoMd_extract_format():
  class fake_video_md (VideoMetaData):
    def __init__ (self, metadata, *args, **kwargs):
      self.metadata = metadata
  
  fake_metadata = {'formats': [
    {}, # some format without audio or video
    { 'tbr': 1, 'format_id': '1', 'acodec': 'm4a', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'm4a', 'video_ext': 'mp4'  },
    { 'tbr': 3, 'format_id': '2', 'acodec': 'none', 'vcodec': 'avi', 'ext': 'avi', 'audio_ext': 'none', 'video_ext': 'avi' },
    { 'tbr': 4, 'format_id': '3', 'acodec': 'mp3', 'vcodec': 'none', 'ext': 'mp3', 'audio_ext': 'mp3', 'video_ext': 'none' },
    { 'tbr': 2, 'format_id': '4', 'acodec': 'none', 'vcodec': 'mp4', 'ext': 'mp4', 'audio_ext': 'none', 'video_ext': 'mp4' }
  ]}
  
  expected_result : TMdFormats = {
    'both': [
      { 'tbr': 1, 'format_id': '1', 'audio': { 'codec': 'm4a', 'ext': 'm4a' }, 'video': { 'codec': 'mp4', 'ext': 'mp4' } }
    ],
    'audio': [
      { 'tbr': 4, 'format_id': '3', 'audio': { 'codec': 'mp3', 'ext': 'mp3' } },
      { 'tbr': 1, 'format_id': '1', 'audio': { 'codec': 'm4a', 'ext': 'm4a' } }
    ],
    'video': [
      { 'tbr': 2, 'format_id': '4', 'video': { 'codec': 'mp4', 'ext': 'mp4' } },
      { 'tbr': 1, 'format_id': '1', 'video': { 'codec': 'mp4', 'ext': 'mp4' } }
    ]
  }
  
  assert fake_video_md(fake_metadata)._extract_format() == expected_result

@patch('src.service.MetaData.getSource')
def test_MetadataOpt_to_ytdlp_opt(get_source_mock:Mock):
  """
    Check important options are contained in the returned dict
  """
  # not bilibili
  opt = MetaDataOpt()
  opt.url = 'url'
  opt.cookie_file_path = 'cookie_file_path'
  
  ret_opt = MetaDataOpt.to_ytdlp_opt(opt)
  assert ret_opt['cookiefile'] == 'cookie_file_path'
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
