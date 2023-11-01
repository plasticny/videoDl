from json import loads as jsonLoads
from pytest import raises as pytestRaises
from unittest.mock import patch

from tests.fakers import fake_CompletedProcess
from src.service.MetaData import MetaData, VideoMetaData, PlaylistMetaData, ErrMessage
from src.dlConfig import dlConfig

# test fetch metadata of youtube video with url
def test_fetchMetaData_video():
  md = MetaData.fetchMetaData(url='https://www.youtube.com/watch?v=zKAxWU4odvE')
  with open('tests/testFiles/test_MetaData/yt_v.json', 'r') as f:
    expected = jsonLoads(f.read())

  assert isinstance(md, VideoMetaData)
  assert md.title == expected['title']
  assert md.url == expected['original_url']

# test fetch metadata of bilibili playlist with config object
def test_fetchMetaData_ls():
  config = dlConfig()
  config.url = 'https://www.bilibili.com/video/BV1bN411s7VT'

  md = MetaData.fetchMetaData(config=config)
  with open('tests/testFiles/test_MetaData/bili_ls.json', 'r') as f:
    expected = jsonLoads(f.read())

  assert isinstance(md, PlaylistMetaData)
  assert md.title == expected['title']
  assert md.url == expected['original_url']
  assert md.playlist_count == expected['playlist_count']

def test_fetchMetaData_no_param():
  with pytestRaises(Exception) as e:
    MetaData.fetchMetaData()
  assert str(e.value) == ErrMessage.NO_PARAM.value

@patch('src.service.MetaData.runCommand')
def test_fetchMetaData_failed(runCommand_mock):
  runCommand_mock.return_value = fake_CompletedProcess(1)
  with pytestRaises(Exception) as e:
    MetaData.fetchMetaData(url='https://www.youtube.com/watch?v=zKAxWU4odvE')
  assert str(e.value) == ErrMessage.GET_METADATA_FAILED.value

def test_VideoMetaData_getVideos():
  metaData = jsonLoads(open('tests/testFiles/test_MetaData/yt_v.json', 'r').read())
  md = VideoMetaData(metaData)

  videos = md.getVideos()
  assert len(videos) == 1
  assert videos[0].title == metaData['title']

def test_PlaylistMetaData_getVideos():
  metaData = jsonLoads(open('tests/testFiles/test_MetaData/bili_ls.json', 'r').read())
  md = PlaylistMetaData(metaData)

  videos = md.getVideos()
  assert len(videos) == metaData['playlist_count']
  
  for idx, v in enumerate(videos):
    assert isinstance(v, VideoMetaData)
    assert v.title == metaData['entries'][idx]['title']