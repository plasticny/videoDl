from pytest import raises as pytestRaises
from unittest.mock import patch

from json import loads as jsonLoads

from src.service.MetaData import fetchMetaData, PlaylistMetaData, VideoMetaData
from src.service.structs import Subtitle

@patch('src.service.MetaData.create_videoMd')
@patch('src.service.MetaData.create_playListMd')
@patch('src.service.MetaData.YoutubeDL')
@patch('src.service.MetaData.getSource')
def test_fetchMetaData_type(getSource_mock, YouTubeDL_mock, create_lsMd_mock, create_vMd_mock):
  """Test the type of metadata returned by fetchMetaData"""
  class fake_ydl:
    def __init__(self, type, *args) -> None:
      self.type = type
    def __enter__(self, *args, **kwargs):
      return self
    def __exit__(self, *args, **kwargs):
      pass
    def extract_info(self, *args, **kwargs):
      pass
    def sanitize_info(self, *args, **kwargs):
      return {'_type': self.type}
  class fake_playlistMd(PlaylistMetaData):
    def __init__(self) -> None:
      pass
  class fake_videoMd(VideoMetaData):
    def __init__(self) -> None:
      pass

  getSource_mock.return_value = 'fake source'
  create_lsMd_mock.return_value = fake_playlistMd()
  create_vMd_mock.return_value = fake_videoMd()

  # test video
  YouTubeDL_mock.return_value = fake_ydl('video')
  assert isinstance(fetchMetaData(url='fake url'), VideoMetaData)

  # test playlist
  YouTubeDL_mock.return_value = fake_ydl('playlist')
  assert isinstance(fetchMetaData(url='fake url'), PlaylistMetaData)

def test_videoMd_getSubtitles():
  """test getSubtitles method of VideoMetaData"""
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
  md = VideoMetaData({'subtitles': subtitle_md})
  assert md.subtitles == expected_sub
  assert md.autoSubtitles == []

  # test subtitle and auto subtitle
  md = VideoMetaData({
    'subtitles': subtitle_md, 
    'automatic_captions': auto_subtitle_md
  })
  assert md.subtitles == expected_sub
  assert md.autoSubtitles == expected_auto_sub

def test_fetch_yt_video():
  """test fetch metadata of a real youtube video with url"""
  md = fetchMetaData(url='https://www.youtube.com/watch?v=zKAxWU4odvE')
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

  md = fetchMetaData(url)
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

def test_fetch_failed():
  with pytestRaises(Exception) as e:
    fetchMetaData(url='invalid url')