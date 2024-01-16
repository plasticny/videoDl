from unittest.mock import patch, Mock

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
    self.subtitles = sub
    self.autoSubtitles = auto_sub

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

@patch('src.section.SubTitleSection.SubTitleSection.batch_select')
@patch('src.section.SubTitleSection.SubTitleSection.one_by_one_select')
@patch('src.section.SubTitleSection.SubTitleSection.autofill_sub')
@patch('src.section.SubTitleSection.get_sub_lang_autofill')
@patch('src.section.SubTitleSection.SubTitleSection.ask_selection_mode')
def test_control_sub_selection (
    ask_mode_mock:Mock,
    get_autofill_mock:Mock, autofill_mock:Mock,
    one_by_one_mock:Mock, batch_mock:Mock
  ):
  class fake_video_md (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  
  section = SubTitleSection()
  
  # autofill
  get_autofill_mock.return_value = True
  section.control_sub_selection([fake_video_md()], {})
  autofill_mock.assert_called_once()
  one_by_one_mock.assert_not_called()
  batch_mock.assert_not_called()
  
  # only one video
  autofill_mock.reset_mock()
  get_autofill_mock.return_value = None
  section.control_sub_selection([fake_video_md()], {})
  autofill_mock.assert_not_called()
  one_by_one_mock.assert_called_once()
  batch_mock.assert_not_called()  
  
  # === multiple video === #
  # choose batch mode
  one_by_one_mock.reset_mock()
  ask_mode_mock.return_value = SelectionMode.BATCH.value
  section.control_sub_selection([fake_video_md(), fake_video_md()], {})
  autofill_mock.assert_not_called()
  one_by_one_mock.assert_not_called()
  batch_mock.assert_called_once()
  
  # choose one by one
  batch_mock.reset_mock()
  ask_mode_mock.return_value = SelectionMode.ONE_BY_ONE.value
  section.control_sub_selection([fake_video_md(), fake_video_md()], {})
  autofill_mock.assert_not_called()
  one_by_one_mock.assert_called_once()
  batch_mock.assert_not_called()  

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

@patch('src.section.SubTitleSection.inq_prompt')
@patch('src.section.SubTitleSection.get_do_write_subtitle_autofill')
def test_ask_write_sub (autofill_mock:Mock, prompt_mock:Mock):
  """ test the autofill work """
  section = SubTitleSection()
  
  autofill_mock.return_value = True
  assert section.ask_write_sub() == True
  prompt_mock.assert_not_called()
  
  autofill_mock.return_value = None
  prompt_mock.return_value = { 'writeSub': 'No' }
  assert section.ask_write_sub() == False
  prompt_mock.assert_called_once()
  
def test_autofill_sub ():
  class fake_video_md (VideoMetaData):
    def __init__ (self, sub, auto_sub, *args, **kwargs):
      self.subtitles = sub
      self.autoSubtitles = auto_sub
  
  sub1 = Subtitle('sub1', 'sub1', False)
  sub2 = Subtitle('sub2', 'sub2', False)
  sub3 = Subtitle('sub3', 'sub3', True)
  
  preferred_code_ls = [sub3.code, sub1.code]
  md_ls : list[VideoMetaData] = [
    fake_video_md(
      sub=[sub1],
      auto_sub=[sub3]
    ),
    fake_video_md(
      sub=[],
      auto_sub=[]
    ),
    fake_video_md(
      sub=[sub2, sub1],
      auto_sub=[]
    )
  ]
  
  res = SubTitleSection().autofill_sub(md_ls, preferred_code_ls)
  assert res == [sub3, None, sub1]

@patch('src.section.SubTitleSection.inq_prompt')
@patch('src.section.SubTitleSection.get_sub_write_mode_autofill')
def test_select_write_mode (autofill_mock:Mock, prompt_mock:Mock):
  section = SubTitleSection()
  
  autofill_mock.return_value = (True, True)
  section.select_write_mode()
  prompt_mock.assert_not_called()
  
  autofill_mock.return_value = None
  section.select_write_mode()
  prompt_mock.assert_called_once()
