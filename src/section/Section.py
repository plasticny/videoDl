import sys

class Section:
  def __init__(self, title):
    self.title = title
  
  @property
  def header (self):
    return f"================= {self.title} ================="
  
  @property
  def footer (self):
    return ''
  
  def run (self, bodyFunc=None):
    sys.stdout.flush()
        
    result = None
    
    print(self.header)
    if callable(bodyFunc):
      result = bodyFunc()
    print(self.footer)
    
    return result
  