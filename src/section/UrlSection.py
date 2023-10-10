from section.Section import Section
from service.urlHelper import isValid, removeSurplusParam

class UrlSection (Section):
  def __init__ (self, title):
    super().__init__(title)
  
  def run (self):
    return super().run(self.__askUrl)
  
  def __askUrl (self):
    while True:
      url = input("Enter the url: ").strip()

      # check if empty url
      if url == '':
        print('Url must not be empty')
        continue

      # check url valid
      valid, err = isValid(url)
      if not(valid):
        print(err)
      else:
        break

    url = removeSurplusParam(url)

    return url
