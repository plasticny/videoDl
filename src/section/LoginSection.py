from section.Section import Section
import tkinter.filedialog as tkFileDialog

# ask the login cookie
class LoginSection(Section):
  def __init__(self, title):
    super().__init__(title)
    
  def run(self):
    return super().run(self.__login)
  
  def __login(self):
    cookieFile = self.__askLogin()
    if cookieFile == None:
        print("Not login")
    else:
        print(f'Login with cookie file: {cookieFile}')
    return cookieFile
  
  def __askLogin(self):
    doLogin = input("Login?(N) ").upper()
    if doLogin == 'N' or doLogin == '':
        return None
    
    print('')
    print('## Select the login cookie file')
    cookieFile = tkFileDialog.askopenfilename(title='Select the login cookie file')
    if len(cookieFile) == 0:
        return None
    return cookieFile