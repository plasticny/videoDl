from colorama import Fore, Style

class Subtitle:
  """
    Subtitle structure
  """
  def __init__(self, code, name, isAuto=False):
    self.code = code
    self.name = name
    self.isAuto = isAuto
  def __str__(self):
    return f'{self.name} {Fore.LIGHTBLACK_EX}{"(Auto gen)" if self.isAuto else ""}{Style.RESET_ALL}'