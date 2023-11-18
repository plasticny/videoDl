from json import loads as jsonLoads
from pytest import raises as pytestRaises

from src.service.MetaData import MetaData, VideoMetaData

# test fetch metadata of youtube video with url
def test_fetch_video():
  md = MetaData.fetchMetaData(url='https://www.youtube.com/watch?v=zKAxWU4odvE')
  with open('tests/testFiles/test_MetaData/yt_v.json', 'r') as f:
    expected = jsonLoads(f.read())

  assert isinstance(md, VideoMetaData)
  assert md.title == expected['title']
  assert md.url == expected['original_url']
  
  assert len(md.subtitles) == 1
  assert md.subtitles[0].code == 'en'
  assert md.subtitles[0].name == 'English'
  assert len(md.autoSubtitles) == 0

# test fetch metadata of bilibili playlist with config object
def test_fetch_bili_ls():
  url = 'https://www.bilibili.com/video/BV1bN411s7VT'

  md = MetaData.fetchMetaData(url)
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
    MetaData.fetchMetaData(url='invalid url')