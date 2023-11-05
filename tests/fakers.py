class fake_CompletedProcess():
  def __init__(self, rc):
    self.rc = rc
  @property
  def returncode(self):
    return self.rc