from urllib.parse import urlparse, parse_qs, urlunparse
from enum import Enum
from requests import get

# website source of the url
class UrlSource (Enum):
  NOT_DEFINED = -1
  YOUTUBE = 0
  YOUTU_BE = 1
  BILIBILI = 2
  PORNHUB = 3
  FACEBOOK = 4
  IG = 5
  PINTEREST = 6
  PIN_IT = 7
  YOUTUBE_LS = 8
  YOUTUBE_SHORT = 9
  X = 10

class SourcePrefix (Enum):
  YOUTUBE = ['youtube.com']
  YOUTU_BE = ['youtu.be']
  YOUTUBE_LS = ['youtube.com/playlist']
  YOUTUBE_SHORT = ['youtube.com/shorts/']
  BILIBILI = ['bilibili.com/video/']
  PORNHUB = ['pornhub.com/view_video.php']
  FACEBOOK = ['facebook.com'] 
  IG = ['instagram.com']
  PINTEREST = ['pinterest.com/pin/']
  PIN_IT = ['pin.it']
  X = ['x.com']

# error message
class ErrMessage (Enum):
  INVALID_URL = 'Invalid url: Not url'
  MISSING_PARAM = 'Invalid url: Missing param {}'

# get the source of the url
def getSource (url : str) -> UrlSource:
  def __check(url:str, prefix:SourcePrefix):
    for p in prefix.value:
      if url.count(p) != 0:
        return True
    return False
  
  prefix_url_map : dict[SourcePrefix, UrlSource] = {
    SourcePrefix.YOUTUBE_LS : UrlSource.YOUTUBE_LS,
    SourcePrefix.YOUTUBE_SHORT : UrlSource.YOUTUBE_SHORT,
    # normal youtube url should be the last to check since it has the most common prefix
    SourcePrefix.YOUTUBE : UrlSource.YOUTUBE,
    SourcePrefix.YOUTU_BE : UrlSource.YOUTU_BE,
    SourcePrefix.BILIBILI : UrlSource.BILIBILI,
    SourcePrefix.PORNHUB : UrlSource.PORNHUB,
    SourcePrefix.FACEBOOK : UrlSource.FACEBOOK,
    SourcePrefix.IG : UrlSource.IG,
    SourcePrefix.PINTEREST : UrlSource.PINTEREST,
    SourcePrefix.PIN_IT : UrlSource.PIN_IT,
    SourcePrefix.X : UrlSource.X
  }
  for prefix, source in prefix_url_map.items():
    if __check(url, prefix):
      return source
  return UrlSource.NOT_DEFINED

# checking if the url is valid
# return: valid (bool), err (str/None)
def isValid (url : str) -> tuple[bool, str]:
  parsedUrl = urlparse(url)

  # check if it is url
  if not(all([parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path])):
    return False, ErrMessage.INVALID_URL.value
           
  source = getSource(url)
  qs = parse_qs(urlparse(url).query)
  if source is UrlSource.YOUTUBE:
    if 'v' not in qs:
      return False, ErrMessage.MISSING_PARAM.value.format('v')
  elif source is UrlSource.YOUTUBE_LS:
    if 'list' not in qs:
      return False, ErrMessage.MISSING_PARAM.value.format('list')
  elif source is UrlSource.PORNHUB:
    if 'viewkey' not in qs:
      return False, ErrMessage.MISSING_PARAM.value.format('viewkey')

  # valid checked
  return True, None

# remove surplus url param that cause download error
# return a url string without those params
def removeSurplusParam (url : str) -> str:
  # helper function
  def keepQuery(url, keepKey : list):
    parsedUrl = urlparse(url)
    queryParams = parse_qs(parsedUrl.query)

    # Remove specified query parameters
    queryParams = {key: value for key, value in queryParams.items() if key in keepKey}

    # Reconstruct the URL without the removed query parameters
    updatedQuery = '&'.join([f"{key}={value[0]}" for key, value in queryParams.items()])
    updatedUrl = urlunparse(parsedUrl._replace(query=updatedQuery))

    return updatedUrl
  
  urlSource = getSource(url)

  if urlSource is UrlSource.YOUTUBE or urlSource is UrlSource.FACEBOOK:
    return keepQuery(url, ['v'])
  if urlSource is UrlSource.YOUTUBE_LS:
    return keepQuery(url, ['list'])
  if urlSource is UrlSource.BILIBILI:
    return keepQuery(url, ['p'])
  if urlSource is UrlSource.PORNHUB:
    return keepQuery(url, ['viewkey'])
  elif urlSource is UrlSource.YOUTU_BE or urlSource is UrlSource.PINTEREST:
    return keepQuery(url, [])

  return url

def redirect (url : str) -> str:
  source = getSource(url)
  if source is not UrlSource.PIN_IT:
    return url

  # pin.it to pinterest  
  k = '"pinId":"'
  html = get(url).text
  srt = html.find(k) + len(k)
  end = html.find('"', srt)
  return 'https://www.pinterest.com/pin/' + html[srt : end]
