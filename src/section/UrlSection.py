from enum import Enum

from section.Section import Section
from service.urlHelper import isValid, removeSurplusParam

class Message(Enum):
  INPUT_URL = 'Enter the url: '
  EMPTY_URL = 'Url must not be empty'

class UrlSection (Section):  
  def run (self):
    return super().run(self.__askUrl)
  
  def __askUrl (self):
    while True:
      url = input(Message.INPUT_URL.value).strip()

      # check if empty url
      if url == '':
        print(Message.EMPTY_URL.value)
        continue

      # check url valid
      valid, err = isValid(url)
      if not(valid):
        print(err)
      else:
        break

    url = removeSurplusParam(url)

    return url
