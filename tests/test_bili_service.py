from unittest.mock import patch, Mock

from src.service.bilibili import get_bili_page_cids, get_bili_subs, _fetch, bvid_2_aid

def test_fetch ():
  """ test no error raised when fetching """
  _fetch('https://api.bilibili.com/x/web-interface/view?bvid=BV1mj411E7eB')

@patch('src.service.bilibili._fetch')
def test_get_bili_page_cids_ng_(fetch_mock:Mock):  
  expected_cids = [1331616732, 1331635717, 1331635546, 1331635521]
  fetch_mock.return_value = {
    'code': 0,
    'data': [ {'cid': cid} for cid in expected_cids ]
  }
    
  bvid = 'bvid'
  cids = get_bili_page_cids(bvid)
  assert bvid in fetch_mock.call_args.args[0]
  assert cids == expected_cids

@patch('src.service.bilibili._fetch')
def test_bili_bvid_2_aid_ng_(fetch_mock:Mock):
  expected_aid = 1331616732
  fetch_mock.return_value = {
    'code': 0,
    'data': {
      'aid': expected_aid
    }
  }
  
  bvid = 'bvid'
  aid = bvid_2_aid(bvid)
  assert bvid in fetch_mock.call_args.args[0]
  assert aid == expected_aid

@patch('src.service.bilibili._fetch')
def test_fetch_bili_subtitle_ng_(fetch_mock:Mock):
  fake_sub1 = {'lan': 'zh-Hans', 'lan_doc': 'Chinese', 'ai_status': 0}
  fake_sub2 = {'lan': 'ja', 'lan_doc': 'Japanese', 'ai_status': 1}

  # [(subtitle list of fetch_ret, bvid, cid, expected_sub, expected_auto_sub)]
  case_ls : list[tuple[list, str, int, list, list]] = [
    ([fake_sub1], 'bvid', None, [fake_sub1], []),
    ([fake_sub1, fake_sub2], 'bvid', 123, [fake_sub1], [fake_sub2])
  ]
  ret = {
    'code': 0,
    'data': {
      'subtitle': {
        'list': []
      }
    }
  }
  
  for case in case_ls:
    print('testing', case)
    fake_fetch_list, bvid, cid, expected_sub, expected_auto_sub = case
    
    ret['data']['subtitle']['list'] = fake_fetch_list
    fetch_mock.return_value = ret
    
    sub, auto_sub = get_bili_subs(bvid, cid=cid)
    
    assert bvid in fetch_mock.call_args.args[0]
    if cid is not None:
      assert str(cid) in fetch_mock.call_args.args[0]

    assert len(sub) == len(expected_sub)
    for expected, actual in zip(expected_sub, sub):
      assert expected['lan'] == actual.code
      assert expected['lan_doc'] == actual.name
      assert expected['ai_status'] == actual.isAutoGen()
      
    assert len(auto_sub) == len(expected_auto_sub)
    for expected, actual in zip(expected_auto_sub, auto_sub):
      assert expected['lan'] == actual.code
      assert expected['lan_doc'] == actual.name
      assert expected['ai_status'] == actual.isAutoGen()
