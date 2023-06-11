from section.Section import Section

class UrlSection (Section):
  def __init__(self, title):
    super().__init__(title)
  
  def run(self):
    return super().run(self.__askUrl)
  
  def __askUrl(self):
    while True:
      url = input("Enter the url: ").strip()
      if url != '':
        break
      print('Url must not be empty')
    return url