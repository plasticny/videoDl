from section.Section import Section
from urllib.parse import urlparse

class UrlSection (Section):
  def __init__ (self, title):
    super().__init__(title)
  
  def run (self):
    return super().run(self.__askUrl)
  
  def __askUrl (self):
    while True:
      url = input("Enter the url: ").strip()

      if url == '':
        print('Url must not be empty')
      elif not(self.__checkUrlValid(url)):
        print('Invalid url')
      else:
        break    
    return url
  
  def __checkUrlValid (self, url):
    try:
      urlparse(url)
      return True
    except:
      return False