from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch

from src.section.LoginSection import LoginSection

@patch('builtins.input', return_value='N')
def test_not_login(print_mock):
  assert LoginSection().run() is None

@patch('builtins.input', return_value='Y')
@patch('tkinter.filedialog.askopenfilename', return_value='cookie.txt')
def test_login(print_mock,_):
  assert LoginSection().run() == 'cookie.txt'

@patch('builtins.input', return_value='Y')
@patch('tkinter.filedialog.askopenfilename', return_value='')
def test_login_canceled(print_mock,_):
  assert LoginSection().run() is None