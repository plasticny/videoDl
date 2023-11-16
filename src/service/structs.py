"""
  Structs
"""
from __future__ import annotations

from colorama import Fore, Style

class Subtitle:
  """
    Structure of VideoMetaData subtitle
  """
  def __init__(self, code, name, isAuto=False):
    self.code : str = code
    self.name : str = name
    self.isAuto : bool = isAuto
  def __str__(self):
    return f'{self.name} {Fore.LIGHTBLACK_EX}{"(Auto gen)" if self.isAuto else ""}{Style.RESET_ALL}'
  def __eq__(self, __value) -> bool:
    if not isinstance(__value, Subtitle):
      return False
    __value:Subtitle = __value
    return self.code == __value.code and self.isAuto == __value.isAuto
  def __hash__(self) -> int:
    return hash(f'{self.code}{self.isAuto}')