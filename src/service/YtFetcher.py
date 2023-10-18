from html.parser import HTMLParser
from requests import get
from enum import Enum
from service.urlHelper import isValid, getSource, UrlSource

class ErrMessage (Enum):
  INVALID_URL = 'Invalid url: Not url'
  NOT_YT_URL = 'Not a youtube url'

# get the title of a youtube song
def getYtSongTitle (url):
  # check if url is valid
  valid, _ = isValid(url)
  if not valid:
    raise ValueError(ErrMessage.INVALID_URL.value)

  # check if url is youtube url
  urlSource = getSource(url)
  if urlSource != UrlSource.YOUTUBE:
    raise ValueError(ErrMessage.NOT_YT_URL.value)

  # get title
  res = get(url)

  class MyHTMLParser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
      super().__init__(convert_charrefs=convert_charrefs)
      self.isTitle = False
      self.title = ""
    def handle_starttag(self, tag, attrs):
      if tag == "title":
        self.isTitle = True
    def handle_endtag(self, tag):
      if tag == "title":
        self.isTitle = False
    def handle_data(self, data):
      if self.isTitle:
        self.title = data

  parser = MyHTMLParser()
  parser.feed(res.text)
  return parser.title[:-10]
