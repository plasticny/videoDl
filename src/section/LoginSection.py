from enum import Enum

from dlConfig import DefaultConfig
from section.Section import Section
import tkinter.filedialog as tkFileDialog

class Message(Enum):
  LOGIN = "Login with cookie file: {}"
  NOT_LOGIN = "Not login"
  ASK_LOGIN = "Login?(N) "
  SELECT_COOKIE_FILE = "## Select the login cookie file"

# ask the login cookie
class LoginSection(Section):
  def __init__(self, title):
    super().__init__(title)
    
  def run(self) -> str:
    return super().run(self.__login)
  
  def __login(self) -> str:
    cookieFile = self.__askLogin()
    if cookieFile == DefaultConfig.cookieFile.value:
      print(Message.NOT_LOGIN.value)
    else:
      print(Message.LOGIN.value.format(cookieFile))
    return cookieFile
  
  def __askLogin(self) -> str:
    doLogin = input(Message.ASK_LOGIN.value).upper()
    if doLogin == 'N' or doLogin == '':
      return DefaultConfig.cookieFile.value
    
    print('')
    print(Message.SELECT_COOKIE_FILE.value)
    cookieFile = tkFileDialog.askopenfilename(title=Message.SELECT_COOKIE_FILE.value)
    if len(cookieFile) == 0:
      return DefaultConfig.cookieFile.value
    return cookieFile