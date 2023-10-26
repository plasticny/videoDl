from src.section.Section import Section, HeaderType

def bodyFunc():
  return 'bodyFunc'

def test_title_show_correct(capfd):
  title = 'Test Section'

  section = Section(title)
  section.doShowFooter = False
  section.run()

  out, err = capfd.readouterr()
  assert out.count(title) == 1
  assert err == ''

def test_show_header(capfd):
  section = Section('Test Section')

  result = section.run(bodyFunc)
  assert result == bodyFunc()
  
  out, err = capfd.readouterr()
  expected_out = section.header + '\n'
  expected_out += section.footer + '\n'
  assert out == expected_out
  assert err == ''

def test_not_show_header_footer(capfd):
  section = Section('Test Section')
  section.doShowHeader = False
  section.doShowFooter = False

  result = section.run(bodyFunc)
  assert result == bodyFunc()
  
  out, err = capfd.readouterr()
  assert out == ''
  assert err == ''

def test_show_subHeader(capfd):
  section = Section('Test Section')
  section.headerType = HeaderType.SUB_HEADER

  result = section.run(bodyFunc)
  assert result == bodyFunc()
  
  out, err = capfd.readouterr()
  expected_out = section.subHeader + '\n'
  expected_out += section.footer + '\n'
  assert out == expected_out
  assert err == ''
