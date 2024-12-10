from __future__ import annotations
from enum import Enum
from tkinter import filedialog as tkFileDialog
from dataclasses import dataclass
from typing import Optional
from inquirer import List, prompt

from src.section.Section import Section
from src.service.autofill import get_login_autofill


class LoginMethod(Enum):
  COOKIE = 'cookie'
  BROWSER = 'browser'

@dataclass
class LoginSectionRet:
  do_login: bool
  cookie_file_path: Optional[str] = None
  browser: Optional[str] = None

# ask the login cookie
class LoginSection(Section):    
  def run(self, url:str) -> LoginSectionRet:
    return super().run(self._login, url=url)
  
  def _login(self, url: str) -> LoginSectionRet:
    autofill_res = get_login_autofill()
    if autofill_res is not None:
      if len(autofill_res[0]) > 0:
        return LoginSectionRet(do_login=True, cookie_file_path=autofill_res[0])
      else:
        return LoginSectionRet(do_login=True, browser=autofill_res[1])

    loginMethod = self._askLogin()
    if loginMethod == 'Not login':
      self.logger.info("Not login")
      print("Not login")
      return LoginSectionRet(do_login=False)

    if loginMethod == LoginMethod.COOKIE.value:
      cookie_file_path = tkFileDialog.askopenfilename(title="## Select the login cookie file")
      if len(cookie_file_path) != 0:
        self.logger.info(f'Login with cookie file: {cookie_file_path}')
        print(f'Login with cookie file: {cookie_file_path}')
        return LoginSectionRet(do_login=True, cookie_file_path=cookie_file_path)
      else:
        self.logger.info("No cookie selected, not login")
        print("No cookie selected, not login")
        return LoginSectionRet(do_login=False)
      
    if loginMethod == LoginMethod.BROWSER.value:
      self.logger.info("Login with browser: firefox")
      return LoginSectionRet(do_login=True, browser='firefox')

    self.logger.error(f'unexpected login method: {loginMethod}')
    raise Exception(f'unexpected login method: {loginMethod}')

  # ask login method
  # None for not login
  def _askLogin(self) -> Optional[str]:
    return prompt([
      List(
        'method',
        message='Select login method',
        choices=[LoginMethod.COOKIE.value, LoginMethod.BROWSER.value, 'Not login']
      )
    ])['method']
