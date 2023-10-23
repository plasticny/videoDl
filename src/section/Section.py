import sys

class Section:
  def __init__(self, title):
    self.title = title
    self.doShowHeader = True
    self.doShowFooter = True
  
  @property
  def header (self):
    return f"================= {self.title} ================="
  
  @property
  def footer (self):
    return ''
    
  def run (self, bodyFunc=None):
    sys.stdout.flush()
        
    result = None
    
    if self.doShowHeader:
      print(self.header)
    if callable(bodyFunc):
      result = bodyFunc()
    if self.doShowFooter:
      print(self.footer)
    
    return result
  