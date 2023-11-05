from sys import path as sysPath
sysPath.append('src')

from unittest.mock import patch, call

from src.section.LoginSection import LoginSection, Message
from src.service.YtDlpHelper import Opts

@patch('builtins.input', return_value='N')
@patch('builtins.print')
def test_not_login(print_mock,_):
  opts:Opts = LoginSection(
    '', doShowFooter=False, doShowHeader=False
  ).run(Opts())
  assert opts()["cookiefile"] == None
  assert print_mock.mock_calls[0] == call(Message.NOT_LOGIN.value)

@patch('builtins.input', return_value='Y')
@patch('tkinter.filedialog.askopenfilename', return_value='cookie.txt')
@patch('builtins.print')
def test_login(print_mock,_,__):
  opts:Opts = LoginSection(
    "", doShowFooter=False, doShowHeader=False
  ).run(Opts())
  assert opts()["cookiefile"] == 'cookie.txt'
  assert print_mock.mock_calls.count(call(Message.LOGIN.value.format('cookie.txt'))) == 1

@patch('builtins.input', return_value='Y')
@patch('tkinter.filedialog.askopenfilename', return_value='')
@patch('builtins.print')
def test_login_canceled(print_mock,_,__):
  opts:Opts = LoginSection(
    "", doShowFooter=False, doShowHeader=False
  ).run(Opts())
  assert opts()["cookiefile"] == None
  assert print_mock.mock_calls.count(call(Message.NOT_LOGIN.value)) == 1