from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch

from src.service.fetcher import *

def test_get_bili_page_cids():
  cids = BiliBiliFetcher.get_page_cids('BV1mj411E7eB')

  expected_cids = [1331616732, 1331635717, 1331635546, 1331635521]
  assert cids == expected_cids

def test_fetch_bili_subtitle():
  sub, auto_sub = BiliBiliFetcher.getSubtitles('BV1XV4y1P7Bm')

  assert len(sub) == 1
  assert sub[0].code == 'zh-Hans'
  assert not sub[0].isAuto

  # there is actually an auto-subtitle
  # but it cannot be fetched cause cookie is needed
  # (and cookie is not provided in case of privacy)
  assert len(auto_sub) == 0

def test_fetch_bili_page_subtitle():
  sub, auto_sub = BiliBiliFetcher.getSubtitles('BV1mj411E7eB', cid=1331635717)

  assert len(sub) == 2
  sub_codes = [s.code for s in sub]
  assert 'zh-CN' in sub_codes
  assert 'ja' in sub_codes

  assert len(auto_sub) == 0

@patch('src.service.fetcher.json_loads')
@patch('src.service.fetcher.build_opener')
@patch('src.service.fetcher.load_cookies')
def test_bili_fetch_failed(_, build_opener_mock, json_loads_mock):
  """Test the code will return empty list when fetch failed"""
  def fake_build_opener(*args, **kwargs):
    class FakeResponse:
      def read(*args, **kwargs):
        return b'{}'
    class FakeOpener:
      def open(*args, **kwargs):
        return FakeResponse()
    return FakeOpener()

  build_opener_mock.side_effect = fake_build_opener
  json_loads_mock.return_value = {'code': 1}

  sub, auto_sub = BiliBiliFetcher.getSubtitles(id='123')

  assert len(sub) == 0
  assert len(auto_sub) == 0