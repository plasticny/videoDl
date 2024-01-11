from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection, SelectionMode
from src.service.MetaData import VideoMetaData, PlaylistMetaData
from src.structs.video_info import Subtitle

class fake_PlayListMetaData(PlaylistMetaData):
  def __init__(self, videos:list[VideoMetaData]=[]):
    self.videos = videos
class fake_VideoMetaData(VideoMetaData):
  @property
  def title(self):
    return 'fake video'
  def __init__(self, sub:list[Subtitle]=[], auto_sub:list[Subtitle]=[]):
    self._sub = sub
    self._auto_sub = auto_sub

@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_noSubFound(map_subs_mock):
  map_subs_mock.return_value = {}
  ret = SubTitleSection().run([fake_VideoMetaData()])
  assert ret['do_write_subtitle'] == False
  assert ret['subtitle_ls'] == [None]
  assert ret['do_burn'] == False
  assert ret['do_embed'] == False
  
@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_notWriteSub(map_subs_mock, ask_write_sub_mock):
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = False
  ret = SubTitleSection('').run([fake_VideoMetaData()])
  assert ret['do_write_subtitle'] == False
  assert ret['subtitle_ls'] == [None]
  assert ret['do_burn'] == False
  assert ret['do_embed'] == False

@patch('src.section.SubTitleSection.SubTitleSection.ask_show_summary', return_value=False)
@patch('src.section.SubTitleSection.SubTitleSection.select_write_mode')
@patch('src.section.SubTitleSection.SubTitleSection.one_by_one_select')
@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_single_video_selection_mode(
    map_subs_mock, ask_write_sub_mock, 
    one_by_one_select_mock, select_write_mode_mock, _
  ):
  """
    test if one by one selection mode is used
    when there is only one video
  """
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = True
  select_write_mode_mock.return_value = (False, False)

  SubTitleSection('').run([fake_VideoMetaData()])
  assert one_by_one_select_mock.called

@patch('src.section.SubTitleSection.SubTitleSection.ask_show_summary', return_value=False)
@patch('src.section.SubTitleSection.SubTitleSection.select_write_mode')
@patch('src.section.SubTitleSection.SubTitleSection.batch_select')
@patch('src.section.SubTitleSection.SubTitleSection.one_by_one_select')
@patch('src.section.SubTitleSection.SubTitleSection.ask_selection_mode')
@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_playlist_selection_mode(
    map_subs_mock, ask_write_sub_mock, ask_selection_mode_mock,
    one_by_one_select_mock, batch_select_mock,
    select_write_mode_mock, _
  ):
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = True
  select_write_mode_mock.return_value = (False, False)

  md_ls = [fake_VideoMetaData(), fake_VideoMetaData()]
  
  # use batch selection mode
  ask_selection_mode_mock.return_value = SelectionMode.BATCH.value
  SubTitleSection('').run(md_ls)
  assert batch_select_mock.called
  assert not one_by_one_select_mock.called

  # use one by one selection mode
  ask_selection_mode_mock.return_value = SelectionMode.ONE_BY_ONE.value
  batch_select_mock.reset_mock()
  one_by_one_select_mock.reset_mock()
  SubTitleSection('').run(md_ls)
  assert not batch_select_mock.called
  assert one_by_one_select_mock.called

@patch('src.section.SubTitleSection.SubTitleSection.select_sub')
def test_one_by_one_select(select_sub_mock):
  """
    Test with 3 cases:
      1. select a subtitle
      2. skip selecting subtitle
      3. no subtitle available
  """
  fake_video_md = fake_VideoMetaData(auto_sub=[Subtitle('en', 'English', True)])
  fake_video_md_no_sub = fake_VideoMetaData()
  video_mds = [fake_video_md, fake_video_md, fake_video_md_no_sub]

  select_sub_mock.side_effect = [
    Subtitle('en', 'English', True),
    None
  ]
  opts_ls = SubTitleSection('').one_by_one_select(video_mds)
  assert len(opts_ls) == 3
  assert select_sub_mock.call_count == 2

@patch('src.section.SubTitleSection.SubTitleSection.select_sub')
def test_batch_select(select_sub_mock):
  # === helpers to mock the select_sub function === #
  selector_obj = None
  def selector(ret_seq:list[int]):
    for i in ret_seq:
      yield i
  def fake_select_sub(subs:list[Subtitle], **_):
    nonlocal selector_obj
    idx = next(selector_obj)
    return None if idx is None else subs[idx]
  select_sub_mock.side_effect = fake_select_sub
  # === helpers to mock the select_sub function === #

  sub1 = Subtitle('sub1', 'sub1', True)
  sub2 = Subtitle('sub2', 'sub2', True)
  sub3 = Subtitle('sub3', 'sub3', True)
  test_video_nm = 4

  # ==== test 1: select subtitle for 2 video and then skip the remaining video ==== #
  sub_pos_map = {
    sub1: [2, 0], # use a unsorted list for testing
    sub2: [1],
    sub3: [2]
  }
  # select sub3 (assign to 2) > select sub1 (assign to 0) > end selection
  selector_obj = selector([2, 0, None])
  res = SubTitleSection().batch_select(sub_pos_map, test_video_nm)
  assert res == [sub1, None, sub3, None]
  
  # ==== test 2: all video have subtitle after first selection ==== #
  sub_pos_map = {
    sub1: [0, 1, 2, 3],
    sub2: [0],
    sub3: [0]
  }
  # select sub 1 (suppose assigned to all video)
  select_sub_mock.reset_mock()
  selector_obj = selector([0])
  res = SubTitleSection('').batch_select(sub_pos_map, test_video_nm)
  assert res == [sub1, sub1, sub1, sub1]
  assert select_sub_mock.call_count == 1

  # ==== test 3: no subtitle left after first selection ==== #
  sub_pos_map = {
    sub1: [0],
    sub2: [0],
    sub3: [0]
  }
  # select sub 1
  select_sub_mock.reset_mock()
  selector_obj = selector([0])
  res = SubTitleSection('').batch_select(sub_pos_map, test_video_nm)
  assert res == [sub1, None, None, None]
  assert select_sub_mock.call_count == 1

def test_map_subs():
  sub1 = Subtitle('sub1', 'sub1', False)
  sub2 = Subtitle('sub2', 'sub2', False)
  sub3 = Subtitle('sub3', 'sub3', True)
  video_mds = [
    fake_VideoMetaData(sub=[sub1, sub2]),
    fake_VideoMetaData(sub=[sub1], auto_sub=[sub3]),
    fake_VideoMetaData(sub=[sub2]),
    fake_VideoMetaData()
  ]

  sub_pos_map = SubTitleSection('').map_subs(video_mds)

  assert len(sub_pos_map) == 3
  assert sub1 in sub_pos_map
  assert sub2 in sub_pos_map
  assert sub3 in sub_pos_map
  assert sub_pos_map[sub1] == [0, 1]
  assert sub_pos_map[sub2] == [0, 2]
  assert sub_pos_map[sub3] == [1]
