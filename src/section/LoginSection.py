from __future__ import annotations
from enum import Enum
from tkinter import filedialog as tkFileDialog

from src.section.Section import Section
from src.service.autofill import get_login_autofill


class Message(Enum):
  LOGIN = "Login with cookie file: {}"
  NOT_LOGIN = "Not login"
  ASK_LOGIN = "Login?(N) "
  SELECT_COOKIE_FILE = "## Select the login cookie file"


# ask the login cookie
class LoginSection(Section):    
  def run(self, url:str) -> str:
    """
      Return the cookie file path if login, else return None
    """
    return super().run(self._login, url=url)
  
  def _login(self, url:str) -> str:    
    autofill_res = get_login_autofill()
    if autofill_res is not None:
      print(f'Cookie path: {autofill_res}')
      return autofill_res
    
    doLogin = self._askLogin()
    if not doLogin:
      print(Message.NOT_LOGIN.value)
      return None

    print('')
    print(Message.SELECT_COOKIE_FILE.value)
    cookie_file_path = tkFileDialog.askopenfilename(title=Message.SELECT_COOKIE_FILE.value)
    if len(cookie_file_path) != 0:
      print(Message.LOGIN.value.format(cookie_file_path))
      return cookie_file_path
    else:
      print(Message.NOT_LOGIN.value)
      return None
  
  # ask if login
  def _askLogin(self) -> bool:
    doLogin = input(Message.ASK_LOGIN.value).upper()
    return doLogin != 'N' and doLogin != ''