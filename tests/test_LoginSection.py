from unittest.mock import patch

from src.dlConfig import DefaultConfig
from src.section.LoginSection import LoginSection, Message

def test_not_login(capfd):
  section = LoginSection("Test Login Section")

  with patch('builtins.input', return_value='N'):
    cookieFile = section.run()
    assert cookieFile == DefaultConfig.cookieFile.value
  
  out, err = capfd.readouterr()
  expectedOut = section.header + '\n'
  expectedOut += Message.NOT_LOGIN.value + '\n'
  expectedOut += section.footer + '\n'
  assert out == expectedOut
  assert err == '' 

def test_login(capfd):
  section = LoginSection("Test Login Section")

  with patch('builtins.input', return_value='Y'):
    with patch('tkinter.filedialog.askopenfilename', return_value='cookie.txt'):
      cookieFile = section.run()
      assert cookieFile == 'cookie.txt'

  out, err = capfd.readouterr()
  expectedOut = section.header + '\n'
  expectedOut += '\n' + Message.SELECT_COOKIE_FILE.value + '\n'
  expectedOut += Message.LOGIN.value.format('cookie.txt') + '\n'
  expectedOut += section.footer + '\n'
  assert out == expectedOut
  assert err == ''

def test_login_canceled(capfd):
  section = LoginSection("Test Login Section")

  with patch('builtins.input', return_value='Y'):
    # simulate the user cancel the file selection
    with patch('tkinter.filedialog.askopenfilename', return_value=''):
      cookieFile = section.run()
      assert cookieFile == DefaultConfig.cookieFile.value

  out, err = capfd.readouterr()
  expectedOut = section.header + '\n'
  expectedOut += '\n' + Message.SELECT_COOKIE_FILE.value + '\n'
  expectedOut += Message.NOT_LOGIN.value + '\n'
  expectedOut += section.footer + '\n'
  assert out == expectedOut
  assert err == ''
