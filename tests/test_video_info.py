from src.structs.video_info import *

def test_subtitle():
  """Test subtitle structure"""
  # Test (Auto gen) is shown if the subtitle is a auto-sub
  sub = Subtitle('en', 'English')
  assert str(sub).count('(Auto gen)') == 0

  auto_sub = Subtitle('en', 'English', True)
  assert str(auto_sub).count('(Auto gen)') == 1

  # Test __eq__
  sub1 = Subtitle('en', 'English')
  sub2 = Subtitle('en', 'Engllsh', True)
  sub3 = Subtitle('en', 'En')
  sub4 = Subtitle('zh', 'Chinese')

  assert sub1 == sub1
  assert sub1 != sub2
  assert sub1 == sub3
  assert sub1 != sub4
  assert sub1 != 'not a subtitle'
  assert sub1 != None

def test_bilibili_subtitle():
  """Test bilibili subtitle structure"""
  # Test __eq__
  sub1 = BiliBiliSubtitle('en', 'English', 0)
  sub2 = BiliBiliSubtitle('en', 'Engllsh', 1)
  sub3 = BiliBiliSubtitle('en', 'English', 2)

  assert sub1 == sub1
  assert sub1 != sub2
  assert sub1 != sub3
  assert sub2 == sub3
  
def test_BundledFormat_eq():
  bundled_format1 = BundledFormat(video='mp4', audio='mp3')
  bundled_format2 = BundledFormat(video='mp4', audio='mp3')
  bundled_format3 = BundledFormat(video='mp4', audio='aac')
  bundled_format4 = BundledFormat(video='mkv', audio='mp3')
  
  # test cases [(format1, format2, expected_result)]  
  case_ls : list[tuple[BundledFormat, BundledFormat, bool]] = [
    (bundled_format1, bundled_format1, True),
    (bundled_format1, bundled_format2, True),
    (bundled_format1, bundled_format3, False),
    (bundled_format2, bundled_format4, False),
    (bundled_format1, 'not a BundledFormat', False),
    (bundled_format1, None, False),
  ]
  
  for case in case_ls:
    print('testing', case)
    case_format1, case_format2, expected_result = case
    assert (case_format1 == case_format2) == expected_result
