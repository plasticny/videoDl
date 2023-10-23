import sys
from enum import Enum

class HeaderType(Enum):
  HEADER = 1
  SUB_HEADER = 2

class Section:
  def __init__(self, title):
    self.title = title
    self.doShowHeader = True
    self.doShowFooter = True

    self.headerType = HeaderType.HEADER
  
  @property
  def header (self):
    return f"================= {self.title} ================="
  
  @property
  def subHeader (self):
    return f"## {self.title}"
  
  @property
  def footer (self):
    return ''
    
  def run (self, bodyFunc=None):
    sys.stdout.flush()
        
    result = None
    
    # header
    if self.doShowHeader:
      if self.headerType == HeaderType.HEADER:
        print(self.header)
      elif self.headerType == HeaderType.SUB_HEADER:
        print(self.subHeader)

    # body
    if callable(bodyFunc):
      result = bodyFunc()

    # footer
    if self.doShowFooter:
      print(self.footer)
    
    return result
  