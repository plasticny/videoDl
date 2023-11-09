from enum import Enum

from section.Section import Section
from service.YtDlpHelper import Opts
import tkinter.filedialog as tkFileDialog

class Message(Enum):
  LOGIN = "Login with cookie file: {}"
  NOT_LOGIN = "Not login"
  ASK_LOGIN = "Login?(N) "
  SELECT_COOKIE_FILE = "## Select the login cookie file"

# ask the login cookie
class LoginSection(Section):    
  def run(self, opts:Opts=Opts()) -> Opts:
    return super().run(self.__login, opts=opts.copy())
  
  # ask if login
  def __askLogin(self) -> bool:
    doLogin = input(Message.ASK_LOGIN.value).upper()
    return doLogin != 'N' and doLogin != ''

  def __login(self, opts:Opts) -> Opts:
    doLogin = self.__askLogin()
    if not doLogin:
      print(Message.NOT_LOGIN.value)
      return opts

    print('')
    print(Message.SELECT_COOKIE_FILE.value)
    cookieFile = tkFileDialog.askopenfilename(title=Message.SELECT_COOKIE_FILE.value)
    if len(cookieFile) != 0:
      opts.cookieFile(cookieFile)
      print(Message.LOGIN.value.format(cookieFile))
    else:
      print(Message.NOT_LOGIN.value)
    
    return opts