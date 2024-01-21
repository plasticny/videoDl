from unittest.mock import patch, Mock

from src.service.bilibili import get_bili_page_cids, get_bili_subs, _fetch, bvid_2_aid

def test_fetch ():
  """ test no error raised when fetching """
  _fetch('https://api.bilibili.com/x/web-interface/view?bvid=BV1mj411E7eB')

@patch('src.service.bilibili._fetch')
def test_get_bili_page_cids(fetch_mock:Mock):
  fetch_mock.return_value = {
    'code': 0,
    'data': [
      {'cid': 1331616732},
      {'cid': 1331635717},
      {'cid': 1331635546},
      {'cid': 1331635521}
    ]
  }
  
  bvid = 'bvid'
  cids = get_bili_page_cids(bvid)
  expected_cids = [1331616732, 1331635717, 1331635546, 1331635521]
  assert bvid in fetch_mock.call_args.args[0]
  assert cids == expected_cids

@patch('src.service.bilibili._fetch')
def test_bili_bvid_2_aid(fetch_mock:Mock):
  fetch_mock.return_value = {
    'code': 0,
    'data': {
      'aid': 1331616732
    }
  }
  
  bvid = 'bvid'
  aid = bvid_2_aid(bvid)
  assert bvid in fetch_mock.call_args.args[0]
  assert aid == 1331616732

@patch('src.service.bilibili._fetch')
def test_fetch_bili_subtitle(fetch_mock:Mock):
  ret = {
    'code': 0,
    'data': {
      'subtitle': {
        'list': [
          {'lan': 'zh-Hans', 'lan_doc': 'Chinese', 'ai_status': 0},
        ]
      }
    }
  }
  
  # test subtitle
  fetch_mock.return_value = ret
  bvid = 'bvid'
  sub, auto_sub = get_bili_subs(bvid)
  assert bvid in fetch_mock.call_args.args[0]
  assert len(sub) == 1
  assert sub[0].code == 'zh-Hans'
  assert sub[0].name == 'Chinese'
  assert sub[0].isAutoGen() == False
  assert len(auto_sub) == 0
  
  # test subtitle when cid is given, and auto subtitle exists
  ret['data']['subtitle']['list'].append({'lan': 'ja', 'lan_doc': 'Japanese', 'ai_status': 1})
  
  fetch_mock.return_value = ret
  bvid = 'bvid'
  cid = 123
  sub, auto_sub = get_bili_subs(bvid, cid=cid)
  assert bvid in fetch_mock.call_args.args[0]
  assert str(cid) in fetch_mock.call_args.args[0]
  assert len(sub) == 1
  assert sub[0].code == 'zh-Hans'
  assert sub[0].name == 'Chinese'
  assert sub[0].isAutoGen() == False
  assert len(auto_sub) == 1
  assert auto_sub[0].code == 'ja'
  assert auto_sub[0].name == 'Japanese'
  assert auto_sub[0].isAutoGen() == True
