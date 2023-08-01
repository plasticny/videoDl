from html.parser import HTMLParser
from requests import get

# get the title of a youtube song
def getYtSongTitle (url):
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
