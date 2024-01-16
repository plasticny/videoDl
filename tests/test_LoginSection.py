from unittest.mock import patch, Mock

from src.section.LoginSection import LoginSection

@patch('builtins.input', return_value='N')
@patch('src.section.LoginSection.get_login_autofill', return_value=None)
def test_not_login(autofill_mock, print_mock):
  assert LoginSection().run('url') is None

@patch('builtins.input', return_value='Y')
@patch('tkinter.filedialog.askopenfilename', return_value='cookie.txt')
@patch('src.section.LoginSection.get_login_autofill', return_value=None)
def test_login(autofill_mock, print_mock, _):
  assert LoginSection().run('url') == 'cookie.txt'

@patch('builtins.input', return_value='Y')
@patch('tkinter.filedialog.askopenfilename', return_value='')
@patch('src.section.LoginSection.get_login_autofill', return_value=None)
def test_login_canceled(autofill_mock, print_mock, _):
  assert LoginSection().run('url') is None

@patch('src.section.LoginSection.LoginSection._askLogin')
@patch('src.section.LoginSection.get_login_autofill')
def test_autofill (autofill_mock:Mock, ask_mock:Mock):
  section = LoginSection()
  ask_mock.return_value = None
  
  # no autofill
  autofill_mock.return_value = None
  section.run('url')
  ask_mock.assert_called_once()
  
  # autofill
  ask_mock.reset_mock()
  autofill_mock.return_value = 'cookie.txt'
  assert section.run('url') == 'cookie.txt'
  ask_mock.assert_not_called()
