from src.service.structs import *

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