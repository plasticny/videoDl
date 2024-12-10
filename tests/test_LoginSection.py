from unittest.mock import patch, Mock
from dataclasses import dataclass
from typing import Optional

from src.section.LoginSection import LoginSection, LoginSectionRet, LoginMethod

@patch('tkinter.filedialog.askopenfilename')
@patch('src.section.LoginSection.LoginSection._askLogin')
@patch('src.section.LoginSection.get_login_autofill')
def test(autofill_mock: Mock, ask_login_mock: Mock, filedialog_mock: Mock):
  @dataclass
  class Case:
    autofill: Optional[tuple[str, str]]
    ask_login_ret: Optional[str]
    filedialog: Optional[str]
    ask_login_called: bool
    expected: LoginSectionRet

  case_ls: list[Case] = [
    # 0: not login
    Case(None, 'Not login', None, True, LoginSectionRet(do_login=False)),
    # 1: use cookie
    Case(None, LoginMethod.COOKIE.value, 'cookie.txt', True, LoginSectionRet(do_login=True, cookie_file_path='cookie.txt')),
    # 2: use cookie canceled
    Case(None, LoginMethod.COOKIE.value, '', True, LoginSectionRet(do_login=False)),
    # 3: use browser
    Case(None, LoginMethod.BROWSER.value, None, True, LoginSectionRet(do_login=True, browser='firefox')),
    # 4: autofil use cookie
    Case(('cookie.txt', ''), None, None, False, LoginSectionRet(do_login=True, cookie_file_path='cookie.txt')),
    # 5: autofil use browser
    Case(('', 'firefox'), None, None, False, LoginSectionRet(do_login=True, browser='firefox')),
  ]

  for idx, case in enumerate(case_ls):
    print(f'Case {idx}')

    autofill_mock.reset_mock()
    ask_login_mock.reset_mock()
    filedialog_mock.reset_mock()

    autofill_mock.return_value = case.autofill
    ask_login_mock.return_value = case.ask_login_ret
    filedialog_mock.return_value = case.filedialog

    actual = LoginSection().run('url')
    assert actual is not None
    for key in case.expected.__annotations__:
      assert getattr(actual, key) == getattr(case.expected, key)
    assert ask_login_mock.called == case.ask_login_called
