from urllib.parse import urlparse, parse_qs, urlunparse
from enum import Enum

# website source of the url
class UrlSource (Enum):
  NOT_DEFINED = -1
  YOUTUBE = 0
  YOUTU_BE = 1
  BILIBILI = 2
  PORNHUB = 3
  FACEBOOK = 4
  IG = 5

class SourcePrefix (Enum):
  YOUTUBE = ['www.youtube.com']
  YOUTU_BE = ['youtu.be']
  BILIBILI = ['www.bilibili.com/video/']
  PORNHUB = ['pornhub.com/view_video.php']
  FACEBOOK = ['www.facebook.com'] 
  IG = ['www.instagram.com']

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

  if __check(url, SourcePrefix.YOUTUBE):
    return UrlSource.YOUTUBE
  elif __check(url, SourcePrefix.YOUTU_BE):
    return UrlSource.YOUTU_BE
  elif __check(url, SourcePrefix.BILIBILI):
    return UrlSource.BILIBILI
  elif __check(url, SourcePrefix.PORNHUB):
    return UrlSource.PORNHUB
  elif __check(url, SourcePrefix.FACEBOOK):
    return UrlSource.FACEBOOK
  elif __check(url, SourcePrefix.IG):
    return UrlSource.IG
  
  return UrlSource.NOT_DEFINED

# checking if the url is valid
# return: valid (bool), err (str/None)
def isValid (url : str) -> (bool, str):
  parsedUrl = urlparse(url)

  # check if it is url
  if not(all([parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path])):
    return False, ErrMessage.INVALID_URL.value
           
  source = getSource(url)
  if source is UrlSource.YOUTUBE or source is UrlSource.FACEBOOK:
    if 'v' not in parse_qs(urlparse(url).query):
      return False, ErrMessage.MISSING_PARAM.value.format('v')
  elif source is UrlSource.PORNHUB:
    if 'viewkey' not in parse_qs(urlparse(url).query):
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
  elif urlSource is UrlSource.BILIBILI:
    return keepQuery(url, ['p'])
  elif urlSource is UrlSource.PORNHUB:
    return keepQuery(url, ['viewkey'])
  
  return url