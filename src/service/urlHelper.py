from urllib.parse import urlparse, parse_qs, urlunparse
from enum import Enum

# website source of the url
class UrlSource (Enum):
  NOT_DEFINED = -1
  YOUTUBE = 0
  BILIBILI = 1

# error message
class ErrMessage (Enum):
  INVALID_URL = 'Invalid url: Not url'
  INVALID_YOUTUBE_URL = 'Invalid url: www.youtube.com url should have the query v'

# checking if the url is valid
# return: valid (bool), err (str/None)
def isValid (url : str) -> (bool, str):
  parsedUrl = urlparse(url)

  # check if it is url
  if not(all([parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path])):
    return False, ErrMessage.INVALID_URL.value
           
  # for 'www.youtube.com' url, check if it contain query 'v'
  if url.count('www.youtube.com') != 0:
    if 'v' not in parse_qs(urlparse(url).query):
      return False, ErrMessage.INVALID_YOUTUBE_URL.value

  # valid checked
  return True, None

# get the source of the url
def getSource (url : str) -> UrlSource:
  # 'www.youtube.com' url
  if url.count('www.youtube.com') != 0:
    return UrlSource.YOUTUBE
  
  # 'www.bilibili.com/video' url
  if url.count('www.bilibili.com/video') != 0:
    return UrlSource.BILIBILI
  
  return UrlSource.NOT_DEFINED

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

  # youtube
  if urlSource == UrlSource.YOUTUBE:
    return keepQuery(url, ['v'])
  # bilibili
  if urlSource == UrlSource.BILIBILI:
    return keepQuery(url, [])
  
  # not defined
  if urlSource == UrlSource.NOT_DEFINED:
    raise NotImplementedError()