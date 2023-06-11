import sys

class Section:
  def __init__(self, title):
    self.title = title
    
  def __header (self):
    return f"================= {self.title} ================="
  
  def __footer (self):
    return ''
  
  def run (self, bodyFunc=None):
    sys.stdout.flush()
        
    result = None
    
    print(self.__header())
    if callable(bodyFunc):
      result = bodyFunc()
    print(self.__footer())
    
    return result
  