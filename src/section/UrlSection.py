from enum import Enum

from src.section.Section import Section
from src.service.urlHelper import isValid, removeSurplusParam, getSource, UrlSource

class Message(Enum):
  INPUT_URL = 'Enter the url: '
  EMPTY_URL = 'Url must not be empty'
  URL_SOURCE_NOT_TESTED = 'Warning: download may fail because this url source is not tested'

class UrlSection (Section):  
  def run (self) -> str:
    return super().run(self.__askUrl)
  
  def __askUrl (self) -> str:
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

    if getSource(url) == UrlSource.NOT_DEFINED:
      print(Message.URL_SOURCE_NOT_TESTED.value)
    else:
      url = removeSurplusParam(url)

    return url
