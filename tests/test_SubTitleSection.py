from unittest.mock import patch, call

from src.section.SubTitleSection import SubTitleSection, VALUE, Message

@patch('builtins.input')
def test_subLang(input_mock):
  section = SubTitleSection('')

  # Test with custom language
  input_mock.return_value = 'zh'
  lang, _ = section.run()
  assert lang == 'zh'

  # Test with default language
  input_mock.return_value = ''
  lang, _ = section.run()
  assert lang == VALUE.DEFAULT_IN_LANG.value

@patch('builtins.input')
def test_doWriteAutoSub(input_mock):
  section = SubTitleSection('')

  # Test with write auto subtitle
  input_mock.return_value = 'Y'
  _, doWriteAutoSub = section.run()
  assert doWriteAutoSub == True

  # Test with not write auto subtitle
  input_mock.return_value = 'N'
  _, doWriteAutoSub = section.run()
  assert doWriteAutoSub == False

@patch('builtins.input')
def test_ui_output(input_mock):
  section = SubTitleSection('')

  # Test with custom language and write auto subtitle
  input_mock.side_effect = ['zh', 'Y']
  section.run()
  input_mock.assert_has_calls([
    call(Message.ASK_LANG.value),
    call(Message.ASK_WRITE_AUTO_SUB.value),
  ])
