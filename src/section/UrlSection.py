from section.Section import Section
from urllib.parse import urlparse, parse_qs, urlunparse

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
      valid, err = self.__checkUrlValid(url)
      if not(valid):
        print(err)
      else:
        break

    url = self.__removeSurplusParam(url)

    return url
  
  # checking if the url is valid
  # return: valid (bool), err (str/None)
  def __checkUrlValid (self, url) -> (str, None):
    # check if it is url
    try:
      urlparse(url)
    except:
      return False, 'Invalid url: Not url'
    
    # for 'www.youtube.com' url, check if it contain query 'v'
    if url.count('www.youtube.com') != 0:
      if 'v' not in parse_qs(urlparse(url).query):
        return False, 'Invalid url: www.youtube.com url should have the query v'

    # valid checked
    return True, None

    
  # remove surplus url param that cause download error
  # return a url string without those params
  def __removeSurplusParam (self, url : str):
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

    # 'www.youtube.com' url
    if url.count('www.youtube.com') != 0:
      url = keepQuery(url, ['v'])
    
    return url