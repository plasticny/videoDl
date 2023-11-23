from sys import path
path.append('src')

from unittest.mock import patch

from src.section.SubTitleSection import SubTitleSection, SelectionMode
from src.service.YtDlpHelper import Opts
from src.service.structs import Subtitle
from src.service.MetaData import VideoMetaData, PlaylistMetaData

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

def check_opts(
    opts:Opts,
    expected_ws:bool, expected_was:bool, expected_lang:str, 
    expected_embed:bool, expected_burn:bool
  ):
  """
    Helper function for checking subtitle options in opts

    Args hints:
      `ws`: writeSubtitles\n
      `was`: writeAutomaticSub\n
      `lang`: subtitlesLang\n
      `embed`: embedSubtitle\n
      `burn`: burnSubtitle
  """
  assert opts.writeSubtitles == expected_ws
  assert opts.writeAutomaticSub == expected_was
  assert opts.subtitlesLang == expected_lang
  assert opts.embedSubtitle == expected_embed
  assert opts.burnSubtitle == expected_burn

@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_noSubFound(map_subs_mock):
  map_subs_mock.return_value = {}
  opts_ls = SubTitleSection('').run(fake_VideoMetaData(), opts_ls=[Opts()])
  assert len(opts_ls) == 1
  check_opts(opts_ls[0], False, False, None, None, None)

@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_notWriteSub(map_subs_mock, ask_write_sub_mock):
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = False
  opts_ls = SubTitleSection('').run(fake_VideoMetaData(), opts_ls=[Opts()])
  assert len(opts_ls) == 1
  check_opts(opts_ls[0], False, False, None, None, None)

@patch('src.section.SubTitleSection.SubTitleSection.select_write_mode')
@patch('src.section.SubTitleSection.SubTitleSection.one_by_one_select')
@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_single_video_selection_mode(
    map_subs_mock, ask_write_sub_mock, 
    one_by_one_select_mock, select_write_mode_mock
  ):
  """
    test if one by one selection mode is used
    when there is only one video
  """
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = True
  select_write_mode_mock.return_value = (False, False)

  # test with single video
  SubTitleSection('').run(fake_VideoMetaData(), opts_ls=[Opts()])
  assert one_by_one_select_mock.called

  # test with playlist containing single video
  one_by_one_select_mock.reset_mock()
  SubTitleSection('').run(fake_PlayListMetaData(videos=[fake_VideoMetaData()]), opts_ls=[Opts()])
  assert one_by_one_select_mock.called

@patch('src.section.SubTitleSection.SubTitleSection.select_write_mode')
@patch('src.section.SubTitleSection.SubTitleSection.batch_select')
@patch('src.section.SubTitleSection.SubTitleSection.one_by_one_select')
@patch('src.section.SubTitleSection.SubTitleSection.ask_selection_mode')
@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_playlist_selection_mode(
    map_subs_mock, ask_write_sub_mock, ask_selection_mode_mock,
    one_by_one_select_mock, batch_select_mock,
    select_write_mode_mock
  ):
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = True
  select_write_mode_mock.return_value = (False, False)

  fake_playlist_md = fake_PlayListMetaData(videos=[fake_VideoMetaData(), fake_VideoMetaData()])

  # use batch selection mode
  ask_selection_mode_mock.return_value = SelectionMode.BATCH.value
  SubTitleSection('').run(fake_playlist_md, opts_ls=[Opts(), Opts()])
  assert batch_select_mock.called
  assert not one_by_one_select_mock.called

  # use one by one selection mode
  ask_selection_mode_mock.return_value = SelectionMode.ONE_BY_ONE.value
  batch_select_mock.reset_mock()
  one_by_one_select_mock.reset_mock()
  SubTitleSection('').run(fake_playlist_md, opts_ls=[Opts(), Opts()])
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
  opts_ls = SubTitleSection('').one_by_one_select(video_mds, [Opts()]*3)
  assert len(opts_ls) == 3
  assert select_sub_mock.call_count == 2

@patch('src.section.SubTitleSection.SubTitleSection.select_sub')
def test_batch_select(select_sub_mock):
  # helpers to mock the select_sub function
  selector_obj = None
  def selector(ret_seq:list[int]):
    for i in ret_seq:
      yield i
  def fake_select_sub(subs:list[Subtitle], **_):
    nonlocal selector_obj
    idx = next(selector_obj)
    return None if idx is None else subs[idx]

  sub1 = Subtitle('sub1', 'sub1', True)
  sub2 = Subtitle('sub2', 'sub2', True)
  sub3 = Subtitle('sub3', 'sub3', True)

  # ==== test 1: select subtitle for 2 video and then skip the remaining video ==== #
  opts_ls = [Opts(), Opts(), Opts(), Opts()]
  sub_pos_map = {
    sub1: [0, 2],
    sub2: [1],
    sub3: [2]
  }
  # assign sub3 to 2 > assign sub1 to 0 > end selection
  selector_obj = selector([2,0,None])
  select_sub_mock.side_effect = fake_select_sub
  res_opts_ls = SubTitleSection('').batch_select(sub_pos_map, opts_ls)

  assert len(res_opts_ls) == 4
  check_opts(res_opts_ls[0], False, True, 'sub1', None, None)
  check_opts(res_opts_ls[1], None, None, None, None, None)
  check_opts(res_opts_ls[2], False, True, 'sub3', None, None)
  check_opts(res_opts_ls[3], None, None, None, None, None)

  # ==== test 2: all video have subtitle after first selection ==== #
  opts_ls = [Opts(), Opts(), Opts(), Opts()]
  sub_pos_map = {
    sub1: [0, 1, 2, 3],
    sub2: [0],
    sub3: [0]
  }
  # select sub 1
  select_sub_mock.reset_mock()
  selector_obj = selector([0])
  select_sub_mock.side_effect = fake_select_sub
  res_opts_ls = SubTitleSection('').batch_select(sub_pos_map, opts_ls)

  assert len(res_opts_ls) == 4
  for opts in res_opts_ls:
    check_opts(opts, False, True, 'sub1', None, None)
  assert select_sub_mock.call_count == 1

  # ==== test 3: no subtitle left after first selection ==== #
  opts_ls = [Opts(), Opts(), Opts(), Opts()]
  sub_pos_map = {
    sub1: [0],
    sub2: [0],
    sub3: [0]
  }
  # select sub 1
  select_sub_mock.reset_mock()
  selector_obj = selector([0])
  select_sub_mock.side_effect = fake_select_sub
  res_opts_ls = SubTitleSection('').batch_select(sub_pos_map, opts_ls)

  assert len(res_opts_ls) == 4
  check_opts(res_opts_ls[0], False, True, 'sub1', None, None)
  for opts in res_opts_ls[1:]:
    check_opts(opts, None, None, None, None, None)
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

@patch('src.section.SubTitleSection.SubTitleSection.select_write_mode')
@patch('src.section.SubTitleSection.SubTitleSection.one_by_one_select')
@patch('src.section.SubTitleSection.SubTitleSection.ask_write_sub')
@patch('src.section.SubTitleSection.SubTitleSection.map_subs')
def test_not_change_param_opts(
    map_subs_mock, ask_write_sub_mock, 
    one_by_one_select_mock, select_write_mode_mock
  ):
  map_subs_mock.return_value = {Subtitle('en', 'English', True): [0]}
  ask_write_sub_mock.return_value = True
  one_by_one_select_mock.return_value = [Opts()]
  select_write_mode_mock.return_value = (True, True)

  opts_ls = [Opts()]
  backup_opts = [opts.copy() for opts in opts_ls]
  ret_opts = SubTitleSection('').run(fake_VideoMetaData(), opts_ls=opts_ls)
  for opts, backup in zip(opts_ls, backup_opts):
    assert opts == backup
  for opts, ret in zip(opts_ls, ret_opts):
    assert opts != ret