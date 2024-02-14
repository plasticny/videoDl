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
  """Test the flow of control_sub_selection function"""
  class fake_video_md (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  
  # test cases [(
  #   video_mds, autofill, selected mode,
  #   expected do autofill, expected do ask mode, expected do one by one, expected do batch
  # )]
  case_ls : list[tuple[
    list[fake_video_md], list[str], str,
    bool, bool, bool, bool
  ]] = [
    # autofill set
    ([fake_video_md()], ['en'], None, True, False, False, False),
    # only one video
    ([fake_video_md()], None, None, False, False, True, False),
    # more than one video and choose one by one
    ([fake_video_md(), fake_video_md()], None, SelectionMode.ONE_BY_ONE.value, False, True, True, False),
    # more than one video and choose batch mode
    ([fake_video_md(), fake_video_md()], None, SelectionMode.BATCH.value, False, True, False, True),
  ]
  
  for case in case_ls:
    print('testing', case)
    case_video_mds, case_autofill, case_mode, exp_do_autofill, exp_do_ask_mode, exp_do_one_by_one, exp_do_batch = case
    
    get_autofill_mock.reset_mock()
    autofill_mock.reset_mock()
    ask_mode_mock.reset_mock()
    one_by_one_mock.reset_mock()
    batch_mock.reset_mock()
    
    get_autofill_mock.return_value = case_autofill
    ask_mode_mock.return_value = case_mode
    
    SubTitleSection().control_sub_selection(case_video_mds, {})
    
    assert autofill_mock.called == exp_do_autofill
    assert ask_mode_mock.called == exp_do_ask_mode
    assert one_by_one_mock.called == exp_do_one_by_one
    assert batch_mock.called == exp_do_batch

@patch('src.section.SubTitleSection.SubTitleSection.select_sub')
def test_one_by_one_select(select_sub_mock):
  """
    Test with 3 cases:
      1. select a subtitle
      2. skip selecting subtitle
      3. no subtitle available
  """
  fake_sub1 = Subtitle('en', 'English', True)
  fake_sub2 = Subtitle('fr', 'French', True)
  fake_video_md1 = fake_VideoMetaData(auto_sub=[fake_sub1, fake_sub2])
  fake_video_md2 = fake_VideoMetaData(auto_sub=[fake_sub1, fake_sub2])
  fake_video_md3 = fake_VideoMetaData()
  
  # 2 video with subtitle and 1 video without subtitle
  video_mds = [fake_video_md1, fake_video_md2, fake_video_md3]
  # first select english subtitle, then skip the second video
  select_sub_mock.side_effect = [fake_sub1, None]
  
  opts_ls = SubTitleSection('').one_by_one_select(video_mds)
  assert opts_ls == [fake_sub1, None, None]
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
  
  # test cases [(
  #   sub_pos_map, selecting sequence, number of fake video, expected result
  # )]
  case_ls : list[tuple[
    dict, list[int], int, list[Subtitle]
  ]] = [
    # select subtitle for 2 video and then skip the remaining video
    # select sub3 (assign to 2) > select sub1 (assign to 0) > end selection
    (
      {
        sub1: [2, 0], # use a unsorted list for testing
        sub2: [1],
        sub3: [2]
      }, [2, 0, None], test_video_nm, [sub1, None, sub3, None]
    ),
    # all video have subtitle after first selection
    # select sub 1 (suppose assigned to all video)
    (
      {
        sub1: [0, 1, 2, 3],
        sub2: [0],
        sub3: [0]
      }, [0], test_video_nm, [sub1, sub1, sub1, sub1]
    ),
    # no subtitle left after first selection
    # select sub 1
    (
      {
        sub1: [0],
        sub2: [0],
        sub3: [0]
      }, [0], test_video_nm, [sub1, None, None, None]
    )
  ]
  
  for case in case_ls:
    print('testing', case)
    case_sub_pos_map, case_select_seq, case_video_nm, exp_res = case
    
    select_sub_mock.reset_mock()
    
    selector_obj = selector(case_select_seq)
    res = SubTitleSection().batch_select(case_sub_pos_map, case_video_nm)
    assert res == exp_res
    assert select_sub_mock.call_count == len(case_select_seq)

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
  # test cases [(autofill, prompt, expected returned value)]
  case_ls : list[tuple[bool, str, bool]] = [
    (True, None, True),
    (False, None, False),
    (None, 'Yes', True),
    (None, 'No', False)
  ]
  
  for case in case_ls:
    print('testing', case)
    case_autofill, case_prompt, exp_ret = case
    
    autofill_mock.reset_mock()
    prompt_mock.reset_mock()
    
    autofill_mock.return_value = case_autofill
    prompt_mock.return_value = {'writeSub': case_prompt}
    
    assert SubTitleSection().ask_write_sub() == exp_ret
    assert prompt_mock.called == (case_autofill is None)
  
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
  # test cases [(autofill(doEmbed, doBurn), prompt(doEmbed, doBurn), expected result(doEmbed, doBurn))]
  case_ls : list[tuple[tuple[bool, bool], list[bool, bool], tuple[bool, bool]]] = [
    ((True, True), None, (True, True)),
    ((False, False), None, (False, False)),
    (None, ['Embed', 'Burn'], (True, True)),
    (None, [], (False, False)),
    (None, ['Embed'], (True, False)),
    (None, ['Burn'], (False, True))
  ]
  
  for case in case_ls:
    print('testing', case)
    case_autofill, case_prompt, exp_res = case
    
    autofill_mock.reset_mock()
    prompt_mock.reset_mock()
    
    autofill_mock.return_value = case_autofill
    prompt_mock.return_value = {'writeMode': case_prompt}
    
    assert SubTitleSection().select_write_mode() == exp_res
    assert prompt_mock.called == (case_autofill is None)
